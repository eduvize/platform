import { useContextSelector } from "use-context-selector";
import { ChatContext } from "@context/chat";
import { ChatTool } from "@models/enums";

export const useLastToolResult = <T>(tool: ChatTool): T | null => {
    const results = useContextSelector(ChatContext, (v) => v.messages);
    const instances = results.reduce((acc, message) => {
        return [
            ...acc,
            ...(message.tool_calls || [])
                .filter((t) => t.tool_name === tool)
                .map((t) => t.arguments),
        ];
    }, [] as any[]);

    return instances.length > 0 ? instances[instances.length - 1] : null;
};
