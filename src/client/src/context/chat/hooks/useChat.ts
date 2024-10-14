import { useContextSelector } from "use-context-selector";
import { ChatContext } from "@context/chat";
import { ChatMessageDto } from "@models/dto";
import { ChatPromptType } from "@models/enums";
import { useEffect } from "react";

interface UseChatReturn {
    instructorId: string;
    messages: ChatMessageDto[];
    processing: boolean;
    sendMessage: (msg: string, hideFromChat?: boolean) => void;
    sendAudio: (audio: ArrayBuffer) => void;
    setInstructor: (id: string) => Promise<void>;
    setPrompt: (prompt: ChatPromptType) => Promise<void>;
    purge: () => void;
}

export const useChat = (prompt?: ChatPromptType): UseChatReturn => {
    const instructorId = useContextSelector(ChatContext, (v) => v.instructorId);
    const sendMessage = useContextSelector(ChatContext, (v) => v.sendMessage);
    const sendAudio = useContextSelector(ChatContext, (v) => v.sendAudio);
    const setInstructor = useContextSelector(
        ChatContext,
        (v) => v.setInstructor
    );
    const setPrompt = useContextSelector(ChatContext, (v) => v.setPrompt);
    const messages = useContextSelector(ChatContext, (v) => v.messages);
    const processing = useContextSelector(ChatContext, (v) => v.isProcessing);
    const reset = useContextSelector(ChatContext, (v) => v.reset);

    useEffect(() => {
        if (!prompt) return;

        setPrompt(prompt);
    }, [prompt]);

    return {
        instructorId: instructorId ?? "",
        messages: messages.filter((x) => x.content),
        sendMessage,
        sendAudio,
        setInstructor,
        setPrompt,
        processing,
        purge: reset,
    };
};
