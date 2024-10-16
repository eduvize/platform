import { useDebouncedState } from "@mantine/hooks";
import React, { useState, useCallback, useRef, useEffect } from "react";
import { createContext } from "use-context-selector";

interface AudioInputContextType {
    isListening: boolean;
    isSpeaking: boolean;
    startListening: (gracePeriodMs: number) => Promise<void>;
    stopListening: (finalize?: boolean) => void;
    sampleRate: number;
    subscribe: (callback: (data: Int16Array) => void) => void;
    unsubscribe: (callback: (data: Int16Array) => void) => void;
}

const defaultValue: AudioInputContextType = {
    isListening: false,
    isSpeaking: false,
    startListening: async () => {},
    stopListening: () => {},
    sampleRate: 44100,
    subscribe: () => {},
    unsubscribe: () => {},
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
    const [sampleRate, setSampleRate] = useState(44100);

    const audioContextRef = useRef<AudioContext | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);
    const sourceNodeRef = useRef<MediaStreamAudioSourceNode | null>(null);
    const processorNodeRef = useRef<ScriptProcessorNode | null>(null);
    const gainNodeRef = useRef<GainNode | null>(null);

    // Use a ref for subscribers instead of state
    const subscribersRef = useRef<Set<(data: Int16Array) => void>>(new Set());

    const stopListening = useCallback(
        (finalize = false) => {
            console.log("Stopping listening");
            if (!isListening) return;

            if (
                processorNodeRef.current &&
                sourceNodeRef.current &&
                gainNodeRef.current
            ) {
                sourceNodeRef.current.disconnect(gainNodeRef.current);
                gainNodeRef.current.disconnect(processorNodeRef.current);
                processorNodeRef.current.disconnect();
            }

            if (mediaStreamRef.current) {
                mediaStreamRef.current
                    .getTracks()
                    .forEach((track) => track.stop());
            }

            setIsListening(false);
            setIsSpeaking(false);

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
            console.log("Starting listening");
            try {
                // Create AudioContext in response to user gesture
                const audioContext = new (window.AudioContext ||
                    (window as any).webkitAudioContext)();
                audioContextRef.current = audioContext;
                setSampleRate(audioContext.sampleRate);
                console.log("Sample rate:", audioContext.sampleRate);

                const stream = await navigator.mediaDevices.getUserMedia({
                    audio: true,
                });
                mediaStreamRef.current = stream;

                sourceNodeRef.current =
                    audioContext.createMediaStreamSource(stream);

                // Create and configure GainNode
                gainNodeRef.current = audioContext.createGain();
                gainNodeRef.current.gain.setValueAtTime(
                    3,
                    audioContext.currentTime
                );

                // Create ScriptProcessorNode
                processorNodeRef.current = audioContext.createScriptProcessor(
                    4096,
                    1,
                    1
                );

                // Set up the audio processing function
                processorNodeRef.current.onaudioprocess = (
                    audioProcessingEvent
                ) => {
                    const inputBuffer = audioProcessingEvent.inputBuffer;
                    const inputData = inputBuffer.getChannelData(0);
                    const floatAudioData = new Float32Array(inputData);

                    // Convert Float32Array to Int16Array (Linear16 format)
                    const int16AudioData = new Int16Array(
                        floatAudioData.length
                    );
                    for (let i = 0; i < floatAudioData.length; i++) {
                        const s = Math.max(-1, Math.min(1, floatAudioData[i]));
                        int16AudioData[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
                    }

                    // Notify subscribers with the Linear16 data
                    subscribersRef.current.forEach((callback) =>
                        callback(int16AudioData)
                    );

                    // Update isSpeaking based on audio activity
                    const isActive = floatAudioData.some(
                        (sample) => Math.abs(sample) > 0.01
                    );
                    setIsSpeaking(isActive);
                };

                // Connect nodes
                sourceNodeRef.current.connect(gainNodeRef.current);
                gainNodeRef.current.connect(processorNodeRef.current);
                processorNodeRef.current.connect(audioContext.destination);

                setIsListening(true);
            } catch (error) {
                console.error("Error starting audio input:", error);
            }
        },
        [isListening]
    );

    /**
     * Subscribes a callback function to receive audio data updates.
     * @param callback - The function to be called with new audio data.
     */
    const subscribe = useCallback((callback: (data: Int16Array) => void) => {
        subscribersRef.current.add(callback);
    }, []);

    /**
     * Unsubscribes a previously subscribed callback function.
     * @param callback - The function to be removed from subscribers.
     */
    const unsubscribe = useCallback((callback: (data: Int16Array) => void) => {
        subscribersRef.current.delete(callback);
    }, []);

    return (
        <AudioInputContext.Provider
            value={{
                isListening,
                isSpeaking,
                startListening,
                stopListening,
                sampleRate,
                subscribe,
                unsubscribe,
            }}
        >
            {children}
        </AudioInputContext.Provider>
    );
};
