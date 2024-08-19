import { useContextSelector } from "use-context-selector";
import { PlaygroundContext } from "../PlaygroundContext";

interface UsePlaygroundStateReturn {
    connected: boolean;
    ready: boolean;
}

export const usePlaygroundState = (): UsePlaygroundStateReturn => {
    const isConnected = useContextSelector(
        PlaygroundContext,
        (v) => v.isConnected
    );
    const isReady = useContextSelector(PlaygroundContext, (v) => v.isReady);

    return {
        connected: isConnected,
        ready: isReady,
    };
};
