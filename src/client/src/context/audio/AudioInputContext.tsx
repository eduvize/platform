import { useDebouncedState } from "@mantine/hooks";
import React, { useState, useCallback, useRef, useEffect } from "react";
import { createContext } from "use-context-selector";

// Import the worker
import AudioWorkerScript from "./AudioWorker?worker";

// Define AudioWorker type
type AudioWorker = Worker;

interface AudioInputContextType {
    isListening: boolean;
    isSpeaking: boolean;
    startListening: (gracePeriodMs: number) => Promise<void>;
    stopListening: (finalize?: boolean) => void;
    audioBuffer: Float32Array | null;
    sampleRate: number;
}

const defaultValue: AudioInputContextType = {
    isListening: false,
    isSpeaking: false,
    startListening: async () => {},
    stopListening: () => {},
    audioBuffer: null,
    sampleRate: 44100,
};

export const AudioInputContext =
    createContext<AudioInputContextType>(defaultValue);

interface AudioInputProviderProps {
    children: React.ReactNode;
}

export const AudioInputProvider: React.FC<AudioInputProviderProps> = ({
    children,
}) => {
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useDebouncedState(false, 100);
    const [audioBuffer, setAudioBuffer] = useState<Float32Array | null>(null);
    const [sampleRate, setSampleRate] = useState(44100);

    const audioContextRef = useRef<AudioContext | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);
    const sourceNodeRef = useRef<MediaStreamAudioSourceNode | null>(null);
    const processorNodeRef = useRef<AudioWorkletNode | null>(null);
    const gainNodeRef = useRef<GainNode | null>(null);
    const workerRef = useRef<AudioWorker | null>(null);

    useEffect(() => {
        // Create the Web Worker
        workerRef.current = new AudioWorkerScript();

        // Set up message handler for the worker
        workerRef.current.onmessage = (event) => {
            if (event.data.isSpeaking !== undefined) {
                setIsSpeaking(event.data.isSpeaking);
            }
            if (event.data.type === "silentBuffer") {
                console.log("Audio buffer contains only silence, discarding.");
                setAudioBuffer(null);
            }
            if (
                event.data.type === "speechBuffer" ||
                event.data.type === "finalBuffer"
            ) {
                console.log("Received non-silent audio buffer, setting.");
                setAudioBuffer(event.data.buffer);
            }
        };

        // Clean up the worker when the component unmounts
        return () => {
            if (workerRef.current) {
                workerRef.current.terminate();
            }
        };
    }, []);

    const stopListening = useCallback(
        (finalize = false) => {
            if (!isListening) return;

            if (processorNodeRef.current && sourceNodeRef.current) {
                sourceNodeRef.current.disconnect(processorNodeRef.current);
                processorNodeRef.current.disconnect();
                processorNodeRef.current.port.onmessage = null;
            }

            if (gainNodeRef.current) {
                gainNodeRef.current.disconnect();
                gainNodeRef.current = null;
            }

            if (mediaStreamRef.current) {
                mediaStreamRef.current
                    .getTracks()
                    .forEach((track) => track.stop());
            }

            setIsListening(false);
            setIsSpeaking(false);

            // If finalize is true, ask the worker to finalize the buffer
            if (finalize && workerRef.current) {
                workerRef.current.postMessage({ type: "finalizeBuffer" });
            }

            // Close the AudioContext
            if (audioContextRef.current) {
                audioContextRef.current.close();
                audioContextRef.current = null;
            }
        },
        [isListening, setIsSpeaking]
    );

    const startListening = useCallback(
        async (gracePeriodMs: number) => {
            if (isListening) return;

            try {
                // Create AudioContext in response to user gesture
                const audioContext = new (window.AudioContext ||
                    (window as any).webkitAudioContext)();
                audioContextRef.current = audioContext;
                setSampleRate(audioContext.sampleRate);

                // Define the AudioWorkletProcessor code
                const processorCode = `
          class AudioProcessor extends AudioWorkletProcessor {
            process(inputs) {
              const input = inputs[0];
              if (input && input.length > 0) {
                const channelData = input[0];
                this.port.postMessage(channelData);
              }
              return true;
            }
          }

          registerProcessor('audio-processor', AudioProcessor);
        `;

                // Create a Blob URL for the processor code
                const blob = new Blob([processorCode], {
                    type: "application/javascript",
                });
                const blobURL = URL.createObjectURL(blob);

                // Add the AudioWorklet module
                await audioContext.audioWorklet.addModule(blobURL);

                // Clean up the Blob URL
                URL.revokeObjectURL(blobURL);

                const stream = await navigator.mediaDevices.getUserMedia({
                    audio: true,
                });
                mediaStreamRef.current = stream;

                sourceNodeRef.current =
                    audioContext.createMediaStreamSource(stream);

                // Create the AudioWorkletNode
                processorNodeRef.current = new AudioWorkletNode(
                    audioContext,
                    "audio-processor",
                    {
                        numberOfOutputs: 1, // Must be 1 to connect to GainNode
                    }
                );

                // Create a GainNode with zero gain to prevent audio output
                gainNodeRef.current = audioContext.createGain();
                gainNodeRef.current.gain.value = 0;

                // Set up the message handler to receive audio data
                processorNodeRef.current.port.onmessage = (event) => {
                    if (workerRef.current) {
                        workerRef.current.postMessage({
                            type: "processAudio",
                            data: event.data,
                        });
                    }
                };

                // Connect nodes
                sourceNodeRef.current.connect(processorNodeRef.current);
                processorNodeRef.current.connect(gainNodeRef.current!);
                gainNodeRef.current.connect(audioContext.destination);

                setIsListening(true);
            } catch (error) {
                console.error("Error starting audio input:", error);
            }
        },
        [isListening]
    );

    return (
        <AudioInputContext.Provider
            value={{
                isListening,
                isSpeaking,
                startListening,
                stopListening,
                audioBuffer,
                sampleRate,
            }}
        >
            {children}
        </AudioInputContext.Provider>
    );
};
