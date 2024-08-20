import { useContextSelector } from "use-context-selector";
import { ChatContext } from "@context/chat";

export const useToolResults = () => {
    const results = useContextSelector(ChatContext, (v) => v.toolResults);

    return results;
};
