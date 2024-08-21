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
    pendingTools: string[];
    toolResults: Record<string, any | null>;
    sendMessage: (message: string) => void;
};

const defaultValue: Context = {
    remotePartyAvatarUrl: null,
    localPartyAvatarUrl: null,
    messages: [],
    pendingTools: [],
    toolResults: {},
    sendMessage: () => {},
};

export const ChatContext = createContext<Context>(defaultValue);

interface ChatProviderProps {
    children: ReactNode;
}

export const ChatProvider = ({ children }: ChatProviderProps) => {
    const [localUser] = useCurrentUser();

    const [instructor] = useInstructor();
    const [pendingToolNames, setPendingToolNames] = useState<string[]>([]);
    const [toolResults, setToolResults] = useState<Record<string, any | null>>(
        {}
    );
    const [receiveBuffer, setReceiveBuffer] = useState<string>("");
    const [messages, setMessages] = useState<ChatMessageDto[]>([]);

    useEffect(() => {
        if (!localUser || !instructor) return;

        ChatApi.getHistory().then((history) => {
            setMessages([
                {
                    is_user: false,
                    content: `Hello, ${localUser.profile.first_name}! Welcome to Eduvize - I'm ${instructor.name}, your instructor.
Now that you've completed the onboarding process, let's get started with planning your first few courses!`,
                    create_at_utc: new Date().toISOString(),
                },
                {
                    is_user: false,
                    content: `Is there anywhere you'd like to start, or would you like me to help identify a good starting point for you?`,
                    create_at_utc: new Date().toISOString(),
                },
                ...history,
            ]);
        });
    }, [localUser, instructor]);

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

    useEffect(() => {
        // Set it on the last message received
        setMessages((prev) => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = {
                ...newMessages[newMessages.length - 1],
                tool_calls: Object.keys(toolResults).map((name) => ({
                    tool_name: name,
                    arguments: toolResults[name],
                })),
            };

            return newMessages;
        });
    }, [toolResults]);

    const handleSendMessage = (message: string) => {
        setMessages((prev) => [
            ...prev,
            {
                is_user: true,
                content: message,
                create_at_utc: new Date().toISOString(),
            },
        ]);

        let receivedText = "";
        let completedToolCalls: Record<string, any> = {};

        ChatApi.sendMessage(
            { message },
            (chunk) => {
                if (chunk.text) {
                    receivedText += chunk.text;
                    setReceiveBuffer(receivedText);
                }

                if (chunk.tools) {
                    setPendingToolNames((prev) => [
                        ...prev,
                        ...chunk
                            .tools!.map((tool) => tool.name)
                            .filter((name) => !prev.includes(name)),
                    ]);

                    for (const tool of chunk.tools) {
                        if (!completedToolCalls[tool.name]) {
                            toolResults[tool.name] = null;
                        }

                        try {
                            const data = JSON.parse(tool.data);
                            completedToolCalls[tool.name] = data;
                        } catch (e) {}
                    }
                }
            },
            () => {
                // Complete
                setPendingToolNames([]);
                setToolResults(completedToolCalls);
            }
        );
    };

    if (!instructor || !localUser) {
        return (
            <Center h="100%">
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
                pendingTools: pendingToolNames,
                toolResults,
                sendMessage: handleSendMessage,
            }}
        >
            {children}
        </ChatContext.Provider>
    );
};
