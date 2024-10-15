import { ChatTool } from "@models/enums";
import { useToolResult } from "./useToolResult";
import { useEffect, DependencyList, useRef } from "react";

/**
 * A custom hook that executes an effect when a tool result is available.
 * It wraps useEffect with the same behavior, allowing additional dependencies.
 * @param tool - The ChatTool to watch for results.
 * @param effect - The effect function to execute when a result is available.
 * @param deps - Optional array of dependencies for the effect.
 */
export const useToolCallEffect = (
    tool: ChatTool,
    effect: (result: any) => void,
    deps: DependencyList = []
) => {
    const cachedResult = useRef<any>(null);
    const result = useToolResult(tool);

    useEffect(() => {
        if (result && result !== cachedResult.current) {
            effect(result);
            cachedResult.current = result;
        }
    }, [result, effect, ...deps]);
};
