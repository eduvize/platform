import { useContextSelector } from "use-context-selector";
import { PlaygroundContext } from "../PlaygroundContext";

interface UseCommandLineReturn {
    sendInput: (input: string) => void;
    resize: (rows: number, columns: number) => void;
    output: string | null;
}

export const useCommandLine = (): UseCommandLineReturn => {
    const sendInput = useContextSelector(PlaygroundContext, (v) => v.sendInput);
    const resize = useContextSelector(PlaygroundContext, (v) => v.resize);
    const output = useContextSelector(PlaygroundContext, (v) => v.output);

    return {
        sendInput,
        resize,
        output,
    };
};
