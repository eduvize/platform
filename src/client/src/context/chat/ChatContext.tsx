import { ChatApi } from "@api";
import { useCurrentUser, useInstructor } from "@context/user/hooks";
import { Center, Loader } from "@mantine/core";
import { ChatMessageDto } from "@models/dto";
import { ReactNode, useEffect, useState } from "react";
import { createContext } from "use-context-selector";

type Context = {
    remotePartyAvatarUrl: string | null;
    localPartyAvatarUrl: string | null;
    messages: ChatMessageDto[];
    sendMessage: (message: string) => void;
};

const defaultValue: Context = {
    remotePartyAvatarUrl: null,
    localPartyAvatarUrl: null,
    messages: [],
    sendMessage: () => {},
};

export const ChatContext = createContext<Context>(defaultValue);

interface ChatProviderProps {
    children: ReactNode;
}

export const ChatProvider = ({ children }: ChatProviderProps) => {
    const [localUser] = useCurrentUser();

    const [instructor] = useInstructor();
    const [receiveBuffer, setReceiveBuffer] = useState<string>("");
    const [messages, setMessages] = useState<ChatMessageDto[]>([]);

    useEffect(() => {
        if (!localUser) return;

        ChatApi.getHistory().then((history) => {
            setMessages(history);
        });
    }, [localUser]);

    useEffect(() => {
        if (receiveBuffer === "") return;

        const lastMessage = messages[messages.length - 1];

        if (!lastMessage.is_user) {
            // Update the most recent message
            setMessages((prev) => {
                const newMessages = [...prev];
                newMessages[newMessages.length - 1] = {
                    ...lastMessage,
                    content: receiveBuffer,
                };

                return newMessages;
            });
        } else {
            setMessages((prev) => [
                ...prev,
                {
                    is_user: false,
                    content: receiveBuffer,
                    create_at_utc: new Date().toISOString(),
                },
            ]);
        }
    }, [receiveBuffer]);

    const handleSendMessage = (message: string) => {
        setMessages((prev) => [
            ...prev,
            {
                is_user: true,
                content: message,
                create_at_utc: new Date().toISOString(),
            },
        ]);

        ChatApi.sendMessage({ message }, (message) => {
            setReceiveBuffer((prev) => prev + message);
        }).finally(() => {
            setReceiveBuffer("");
        });
    };

    if (!instructor || !localUser) {
        return (
            <Center>
                <Loader size="lg" type="dots" />
            </Center>
        );
    }

    return (
        <ChatContext.Provider
            value={{
                remotePartyAvatarUrl: instructor.avatar_url,
                localPartyAvatarUrl: localUser.profile?.avatar_url,
                messages,
                sendMessage: handleSendMessage,
            }}
        >
            {children}
        </ChatContext.Provider>
    );
};
