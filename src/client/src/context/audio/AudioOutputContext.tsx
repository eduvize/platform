import React, { createContext, useRef, useCallback, useEffect } from "react";

type Context = {
    playAudio: (audioData: string) => void;
    setVolume: (volume: number) => void;
    stopPlayback: () => void;
};

const defaultValue: Context = {
    playAudio: () => {},
    setVolume: () => {},
    stopPlayback: () => {},
};

export const AudioOutputContext = createContext<Context>(defaultValue);

interface AudioOutputProviderProps {
    children: React.ReactNode;
}

export const AudioOutputProvider: React.FC<AudioOutputProviderProps> = ({
    children,
}) => {
    const audioContextRef = useRef<AudioContext | null>(null);
    const audioQueueRef = useRef<Uint8Array[]>([]);
    const isPlayingAudioRef = useRef<boolean>(false);
    const gainNodeRef = useRef<GainNode | null>(null);
    const currentSourceRef = useRef<AudioBufferSourceNode | null>(null);

    useEffect(() => {
        audioContextRef.current = new (window.AudioContext ||
            (window as any).webkitAudioContext)();
        gainNodeRef.current = audioContextRef.current.createGain();
        gainNodeRef.current.connect(audioContextRef.current.destination);
        return () => {
            audioContextRef.current?.close();
        };
    }, []);

    const stopPlayback = useCallback(() => {
        if (currentSourceRef.current) {
            currentSourceRef.current.stop();
            currentSourceRef.current.onended = null;
        }
        audioQueueRef.current = [];
        isPlayingAudioRef.current = false;
        console.log("Playback stopped");
    }, []);

    const playNextAudioChunk = useCallback(() => {
        if (!audioContextRef.current || audioQueueRef.current.length === 0) {
            isPlayingAudioRef.current = false;
            console.log("Audio queue empty or context not available");
            return;
        }

        const audioData = audioQueueRef.current.shift()!;
        audioContextRef.current.decodeAudioData(
            audioData.buffer,
            (buffer) => {
                const source = audioContextRef.current!.createBufferSource();
                source.buffer = buffer;
                source.connect(gainNodeRef.current!);
                source.onended = playNextAudioChunk;
                source.start();
                currentSourceRef.current = source; // Store the current source
                console.log("Started playing audio chunk");
            },
            (error) => {
                console.error("Error decoding audio data:", error);
                playNextAudioChunk(); // Move to next chunk if there's an error
            }
        );
    }, []);

    const playAudio = useCallback(
        (audioData: string) => {
            console.log("Received audio data, length:", audioData.length);
            const uint8Array = base64ToUint8Array(audioData);
            audioQueueRef.current.push(uint8Array);

            if (!isPlayingAudioRef.current) {
                isPlayingAudioRef.current = true;
                playNextAudioChunk();
            }
        },
        [playNextAudioChunk]
    );

    const setVolume = useCallback((volume: number) => {
        if (gainNodeRef.current) {
            gainNodeRef.current.gain.setValueAtTime(
                volume,
                audioContextRef.current!.currentTime
            );
            console.log("Volume set to:", volume);
        }
    }, []);

    return (
        <AudioOutputContext.Provider
            value={{ playAudio, setVolume, stopPlayback }}
        >
            {children}
        </AudioOutputContext.Provider>
    );
};

// Utility function to convert base64 to Uint8Array
function base64ToUint8Array(base64: string): Uint8Array {
    const binaryString = atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes;
}
