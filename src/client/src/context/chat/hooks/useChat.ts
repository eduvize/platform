import { useContextSelector } from "use-context-selector";
import { ChatContext } from "@context/chat";
import { ChatMessageDto } from "@models/dto";
import { ChatPromptType } from "@models/enums";

interface UseChatReturn {
    instructorId: string;
    messages: ChatMessageDto[];
    processing: boolean;
    sendMessage: (msg: string, hideFromChat?: boolean) => void;
    setInstructor: (id: string) => void;
    setPrompt: (prompt: ChatPromptType) => Promise<void>;
    purge: () => void;
}

export const useChat = (): UseChatReturn => {
    const instructorId = useContextSelector(ChatContext, (v) => v.instructorId);
    const sendMessage = useContextSelector(ChatContext, (v) => v.sendMessage);
    const setInstructor = useContextSelector(
        ChatContext,
        (v) => v.setInstructor
    );
    const setPrompt = useContextSelector(ChatContext, (v) => v.setPrompt);
    const messages = useContextSelector(ChatContext, (v) => v.messages);
    const processing = useContextSelector(ChatContext, (v) => v.isProcessing);
    const reset = useContextSelector(ChatContext, (v) => v.reset);

    return {
        instructorId: instructorId || "",
        messages: messages.filter((x) => x.content),
        sendMessage,
        setInstructor,
        setPrompt,
        processing,
        purge: reset,
    };
};
