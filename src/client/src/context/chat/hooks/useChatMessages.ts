import { useContextSelector } from "use-context-selector";
import { ChatContext } from "@context/chat";
import { ChatMessageDto } from "@models/dto";

interface UseChatMessagesReturn {
    messages: ChatMessageDto[];
    sendMessage: (msg: string) => void;
    processing: boolean;
}

export const useChatMessages = (): UseChatMessagesReturn => {
    const sendMessage = useContextSelector(ChatContext, (v) => v.sendMessage);
    const messages = useContextSelector(ChatContext, (v) => v.messages);
    const processing = useContextSelector(ChatContext, (v) => v.isProcessing);

    return {
        messages: messages.filter((x) => x.content),
        sendMessage,
        processing,
    };
};
