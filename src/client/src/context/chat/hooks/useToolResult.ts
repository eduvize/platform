import { useContextSelector } from "use-context-selector";
import { ChatContext } from "@context/chat";
import { ChatTool } from "@models/enums";
import { useMemo } from "react";

/**
 * A hook to get and cache the result of a specific chat tool.
 * @param tool - The ChatTool to get the result for.
 * @returns The cached result of the specified tool, or null if not available.
 */
export const useToolResult = (tool: ChatTool): any | null => {
    const results = useContextSelector(ChatContext, (v) => v.toolResults);

    return useMemo(() => {
        if (results[tool]) {
            const result =
                typeof results[tool] === "string"
                    ? JSON.parse(results[tool])
                    : results[tool];

            // Use JSON.stringify for deep comparison
            return JSON.parse(JSON.stringify(result));
        }
        return null;
    }, [results[tool]]); // Only depend on the specific tool result
};
