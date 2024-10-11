import { useContextSelector } from "use-context-selector";
import { ChatContext } from "@context/chat";
import { ChatMessageDto } from "@models/dto";

interface UseChatReturn {
    instructorId: string;
    messages: ChatMessageDto[];
    processing: boolean;
    sendMessage: (msg: string) => void;
    purge: () => void;
}

export const useChat = (): UseChatReturn => {
    const instructorId = useContextSelector(ChatContext, (v) => v.instructorId);
    const sendMessage = useContextSelector(ChatContext, (v) => v.sendMessage);
    const messages = useContextSelector(ChatContext, (v) => v.messages);
    const processing = useContextSelector(ChatContext, (v) => v.isProcessing);
    const reset = useContextSelector(ChatContext, (v) => v.reset);

    return {
        instructorId: instructorId || "",
        messages: messages.filter((x) => x.content),
        sendMessage,
        processing,
        purge: reset,
    };
};
