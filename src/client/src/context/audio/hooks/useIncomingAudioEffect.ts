import { useEffect } from "react";
import { useContextSelector } from "use-context-selector";
import { AudioInputContext } from "../AudioInputContext";

/**
 * A custom hook that subscribes to incoming audio data and calls a callback function with the data.
 * It automatically unsubscribes when the component unmounts.
 *
 * @param callback - A function that will be called with the incoming audio data
 * @returns The sample rate of the audio data
 */
export const useIncomingAudioEffect = (
    callback: (data: Int16Array) => void
) => {
    const sampleRate = useContextSelector(
        AudioInputContext,
        (context) => context.sampleRate
    );
    const subscribe = useContextSelector(
        AudioInputContext,
        (context) => context.subscribe
    );
    const unsubscribe = useContextSelector(
        AudioInputContext,
        (context) => context.unsubscribe
    );

    useEffect(() => {
        subscribe(callback);

        return () => {
            unsubscribe(callback);
        };
    }, [callback, subscribe, unsubscribe]);

    return sampleRate;
};
