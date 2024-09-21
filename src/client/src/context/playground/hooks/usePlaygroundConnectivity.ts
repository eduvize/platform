import { useContextSelector } from "use-context-selector";
import { PlaygroundContext } from "../PlaygroundContext";

interface UsePlaygroundConnectivityReturn {
    connected: boolean;
    state: "initializing" | "ready" | null;
    status: string | null;
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
        const state = useContextSelector(
            PlaygroundContext,
            (v) => v.instanceState
        );
        const status = useContextSelector(
            PlaygroundContext,
            (v) => v.setupStatus
        );

        return {
            connected: isConnected,
            state,
            status,
            reconnecting: isReconnecting,
        };
    };
