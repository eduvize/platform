import { ChatApi } from "@api";
import { useCurrentUser } from "@context/user/hooks";
import { Center, Loader } from "@mantine/core";
import { ChatMessageDto } from "@models/dto";
import { ChatPromptType } from "@models/enums";
import { ReactNode, useEffect, useState } from "react";
import { createContext } from "use-context-selector";

type Context = {
    localPartyAvatarUrl: string | null;
    messages: ChatMessageDto[];
    pendingTools: string[];
    toolResults: Record<string, any | null>;
    isProcessing: boolean;
    setGreeting: (greeting: string) => void;
    sendMessage: (message: string) => void;
    reset: () => void;
};

const defaultValue: Context = {
    localPartyAvatarUrl: null,
    messages: [],
    pendingTools: [],
    toolResults: {},
    isProcessing: false,
    setGreeting: () => {},
    sendMessage: () => {},
    reset: () => {},
};

export const ChatContext = createContext<Context>(defaultValue);

interface ChatProviderProps {
    prompt: ChatPromptType;
    resourceId?: string;
    children: ReactNode;
}

export const ChatProvider = ({
    prompt,
    resourceId,
    children,
}: ChatProviderProps) => {
    const [localUser] = useCurrentUser();

    const [pendingToolNames, setPendingToolNames] = useState<string[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [toolResults, setToolResults] = useState<Record<string, any | null>>(
        {}
    );
    const [receiveBuffer, setReceiveBuffer] = useState<string>("");
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [greeting, setGreeting] = useState<string>("");
    const [messages, setMessages] = useState<ChatMessageDto[]>([]);

    const handleSetup = () => {
        ChatApi.createSession(prompt, resourceId).then(({ session_id }) => {
            setSessionId(session_id);

            if (greeting) {
                setMessages([
                    {
                        is_user: false,
                        content: greeting,
                        create_at_utc: new Date().toISOString(),
                    },
                ]);
            }
        });
    };

    useEffect(() => {
        handleSetup();
    }, []);

    useEffect(() => {
        if (greeting) {
            setMessages([
                {
                    is_user: false,
                    content: greeting,
                    create_at_utc: new Date().toISOString(),
                },
            ]);
        }
    }, [greeting]);

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
        if (isProcessing || !sessionId) return;

        setIsProcessing(true);

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
            sessionId,
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
                setIsProcessing(false);
            }
        );
    };

    if (!sessionId || !localUser) {
        return (
            <Center>
                <Loader type="dots" />
            </Center>
        );
    }

    return (
        <ChatContext.Provider
            value={{
                localPartyAvatarUrl: localUser.profile?.avatar_url,
                messages,
                pendingTools: pendingToolNames,
                toolResults,
                isProcessing,
                setGreeting: setGreeting,
                sendMessage: handleSendMessage,
                reset: handleSetup,
            }}
        >
            {children}
        </ChatContext.Provider>
    );
};
