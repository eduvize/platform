import { useContextSelector } from "use-context-selector";
import { ChatContext } from "@context/chat";
import { ChatMessageDto } from "@models/dto";
import { useEffect } from "react";

interface UseChatReturn {
    instructorId: string;
    messages: ChatMessageDto[];
    processing: boolean;
    sendMessage: (msg: string) => void;
    purge: () => void;
}

export const useChat = (greeting?: string): UseChatReturn => {
    const instructorId = useContextSelector(ChatContext, (v) => v.instructorId);
    const sendMessage = useContextSelector(ChatContext, (v) => v.sendMessage);
    const messages = useContextSelector(ChatContext, (v) => v.messages);
    const processing = useContextSelector(ChatContext, (v) => v.isProcessing);
    const setGreeting = useContextSelector(ChatContext, (v) => v.setGreeting);
    const reset = useContextSelector(ChatContext, (v) => v.reset);

    useEffect(() => {
        if (greeting) {
            setGreeting(greeting);
        }
    }, []);

    return {
        instructorId: instructorId || "",
        messages: messages.filter((x) => x.content),
        sendMessage,
        processing,
        purge: reset,
    };
};
