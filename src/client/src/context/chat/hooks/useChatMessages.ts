import { useContextSelector } from "use-context-selector";
import { ChatContext } from "@context/chat";
import { ChatMessageDto } from "@models/dto";

export const useChatMessages = (): [
    ChatMessageDto[],
    (msg: string) => void
] => {
    const sendMessage = useContextSelector(ChatContext, (v) => v.sendMessage);
    const messages = useContextSelector(ChatContext, (v) => v.messages);

    return [messages, sendMessage];
};
