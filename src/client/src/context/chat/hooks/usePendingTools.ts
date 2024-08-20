import { useContextSelector } from "use-context-selector";
import { ChatContext } from "@context/chat";

export const usePendingTools = () => {
    const names = useContextSelector(ChatContext, (v) => v.pendingTools);

    return names;
};
