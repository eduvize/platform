import { useContextSelector } from "use-context-selector";
import { PlaygroundContext } from "../PlaygroundContext";

interface UseCommandLineReturn {
    sendInput: (input: string) => void;
    resize: (rows: number, columns: number) => void;
    subscribe: (callback: (output: string) => void) => void;
    unsubscribe: (callback: (output: string) => void) => void;
}

export const useCommandLine = (): UseCommandLineReturn => {
    const sendInput = useContextSelector(PlaygroundContext, (v) => v.sendInput);
    const resize = useContextSelector(PlaygroundContext, (v) => v.resize);
    const subscribeToOutput = useContextSelector(
        PlaygroundContext,
        (v) => v.subscribeToOutput
    );
    const unsubscribeFromOutput = useContextSelector(
        PlaygroundContext,
        (v) => v.unsubscribeFromOutput
    );

    return {
        sendInput,
        resize,
        subscribe: subscribeToOutput,
        unsubscribe: unsubscribeFromOutput,
    };
};
