import { ChatApi } from "@api";
import { useCurrentUser, useInstructor } from "@context/user/hooks";
import { ChatMessageDto } from "@models/dto";
import { ReactNode, useEffect, useRef, useState } from "react";
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
    const displayedFirstMessageRef = useRef(false);
    const [localUser] = useCurrentUser();

    const [remotePartyAvatarUrl, setRemotePartyAvatarUrl] = useState<string>(
        "http://localhost:9000/eduvize/instructor-assets/6a8bce5d48a34c7cac0e02099a5bc867.png"
    );

    const [localPartyAvatarUrl, setLocalPartyAvatarUrl] = useState<
        string | null
    >(null);
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
        if (localUser?.profile.avatar_url) {
            setLocalPartyAvatarUrl(localUser.profile.avatar_url);
        }
    }, [localUser?.profile.avatar_url]);

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

    return (
        <ChatContext.Provider
            value={{
                remotePartyAvatarUrl,
                localPartyAvatarUrl,
                messages,
                sendMessage: handleSendMessage,
            }}
        >
            {children}
        </ChatContext.Provider>
    );
};
