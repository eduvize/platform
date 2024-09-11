import { useContextSelector } from "use-context-selector";
import { PlaygroundContext } from "../PlaygroundContext";

interface UsePlaygroundConnectivityReturn {
    connected: boolean;
    ready: boolean;
    reconnecting: boolean;
}

export const usePlaygroundConnectivity =
    (): UsePlaygroundConnectivityReturn => {
        const isConnected = useContextSelector(
            PlaygroundContext,
            (v) => v.isConnected
        );
        const isReconnecting = useContextSelector(
            PlaygroundContext,
            (v) => v.isReconnecting
        );
        const isReady = useContextSelector(PlaygroundContext, (v) => v.isReady);

        return {
            connected: isConnected,
            ready: isReady,
            reconnecting: isReconnecting,
        };
    };
