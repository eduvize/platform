import React, { useState, useCallback, useRef } from "react";
import { createContext } from "use-context-selector";
import { useDebouncedCallback } from "@mantine/hooks";

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
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [audioBuffer, setAudioBuffer] = useState<Float32Array | null>(null);
    const [sampleRate, setSampleRate] = useState(44100);

    const audioContextRef = useRef<AudioContext | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);
    const sourceNodeRef = useRef<MediaStreamAudioSourceNode | null>(null);
    const processorNodeRef = useRef<AudioWorkletNode | null>(null);
    const gainNodeRef = useRef<GainNode | null>(null);

    const bufferRef = useRef<Float32Array>(new Float32Array());

    const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    const isBufferSilent = useCallback(
        (buffer: Float32Array, threshold: number = 0.01) => {
            for (let i = 0; i < buffer.length; i++) {
                if (Math.abs(buffer[i]) > threshold) {
                    return false;
                }
            }
            return true;
        },
        []
    );

    const stopListening = useCallback(
        (finalize = false) => {
            if (!isListening) return;

            if (silenceTimeoutRef.current) {
                clearTimeout(silenceTimeoutRef.current);
                silenceTimeoutRef.current = null;
            }

            if (processorNodeRef.current && sourceNodeRef.current) {
                sourceNodeRef.current.disconnect(processorNodeRef.current);
                processorNodeRef.current.disconnect();
                processorNodeRef.current.port.onmessage = null; // Clean up the message handler
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

            // If finalize is true, check if the buffer is not silent before setting it
            if (finalize) {
                if (!isBufferSilent(bufferRef.current)) {
                    setAudioBuffer(bufferRef.current);
                } else {
                    console.log(
                        "Audio buffer contains only silence, discarding."
                    );
                }
            }

            // Close the AudioContext
            if (audioContextRef.current) {
                audioContextRef.current.close();
                audioContextRef.current = null;
            }
        },
        [isListening, isBufferSilent]
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

                // Clear any previous buffer and timers
                bufferRef.current = new Float32Array();
                if (silenceTimeoutRef.current) {
                    clearTimeout(silenceTimeoutRef.current);
                    silenceTimeoutRef.current = null;
                }

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
                    const input = event.data as Float32Array;

                    // Append input to bufferRef
                    const newBuffer = new Float32Array(
                        bufferRef.current.length + input.length
                    );
                    newBuffer.set(bufferRef.current);
                    newBuffer.set(input, bufferRef.current.length);
                    bufferRef.current = newBuffer;

                    // Process the chunk to determine if it's speech or silence
                    const amplitudeThreshold = 0.06; // Adjust as needed

                    let maxAmplitude = 0;
                    for (let i = 0; i < input.length; i++) {
                        const absSample = Math.abs(input[i]);
                        if (absSample > maxAmplitude) {
                            maxAmplitude = absSample;
                        }
                    }

                    const isSpeech = maxAmplitude > amplitudeThreshold;

                    if (isSpeech) {
                        // Speech detected
                        // Reset the silence timer
                        if (silenceTimeoutRef.current) {
                            clearTimeout(silenceTimeoutRef.current);
                            silenceTimeoutRef.current = null;
                        }

                        // Set isSpeaking to true
                        setIsSpeaking(true);
                    } else {
                        // Silence detected
                        if (!silenceTimeoutRef.current) {
                            // Start the silence timer
                            silenceTimeoutRef.current = setTimeout(() => {
                                // Check if the buffer is not silent before finalizing
                                if (!isBufferSilent(bufferRef.current)) {
                                    setAudioBuffer(bufferRef.current);
                                } else {
                                    console.log(
                                        "Audio buffer contains only silence, discarding."
                                    );
                                }

                                bufferRef.current = new Float32Array();
                            }, gracePeriodMs);

                            // Set isSpeaking to false
                            setIsSpeaking(false);
                        }
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
        [isListening, stopListening, isBufferSilent]
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
