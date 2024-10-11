import { ChatApi } from "@api";
import { useCurrentUser } from "@context/user/hooks";
import { Center, Loader } from "@mantine/core";
import { ChatMessageDto } from "@models/dto";
import { ChatPromptType } from "@models/enums";
import { ReactNode, useEffect, useState, useCallback, useRef } from "react";
import { createContext } from "use-context-selector";

type Context = {
    localPartyAvatarUrl: string | null;
    instructorId: string | null;
    messages: ChatMessageDto[];
    pendingTools: string[];
    toolResults: Record<string, any | null>;
    isProcessing: boolean;
    sendMessage: (message: string, hideFromChat?: boolean) => void;
    setInstructor: (instructorId: string) => void;
    setPrompt: (prompt: ChatPromptType) => Promise<void>;
    reset: () => void;
};

const defaultValue: Context = {
    localPartyAvatarUrl: null,
    instructorId: null,
    messages: [],
    pendingTools: [],
    toolResults: {},
    isProcessing: false,
    sendMessage: () => {},
    setInstructor: () => {},
    setPrompt: () => Promise.resolve(),
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
    const [instructorId, setInstructorId] = useState<string | null>(
        resourceId ?? null
    );
    const [currentPrompt, setCurrentPrompt] = useState<ChatPromptType>(prompt);
    const [receiveBuffer, setReceiveBuffer] = useState<string>("");
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [messages, setMessages] = useState<ChatMessageDto[]>([]);
    const incomingMessageCompleteRef = useRef(true);

    const handleSetup = useCallback(async () => {
        return await ChatApi.createSession(
            currentPrompt,
            instructorId ?? undefined
        ).then(({ id: session_id, instructor_id }) => {
            setSessionId(session_id);
            setInstructorId(instructor_id);
            setMessages([]);
        });
    }, [currentPrompt, instructorId]);

    useEffect(() => {
        handleSetup();
    }, [handleSetup]);

    useEffect(() => {
        if (messages.length === 0) {
            sendMessage("Hello!");
        }
    }, [messages]);

    useEffect(() => {
        if (receiveBuffer === "") return;

        const lastMessage = messages[messages.length - 1];

        if (lastMessage && !lastMessage.is_user) {
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
    }, [receiveBuffer, messages]);

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

    const sendMessage = (message: string) => {
        if (!sessionId || !incomingMessageCompleteRef.current) return;

        let receivedText = "";
        let completedToolCalls: Record<string, any> = {};

        incomingMessageCompleteRef.current = false;
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
                incomingMessageCompleteRef.current = true;
                setPendingToolNames([]);
                setToolResults(completedToolCalls);
                setIsProcessing(false);
            }
        );
    };

    const handleSendMessage = (message: string, hideFromChat?: boolean) => {
        if (isProcessing || !sessionId) return;

        setIsProcessing(true);

        if (!hideFromChat) {
            setMessages((prev) => [
                ...prev,
                {
                    is_user: true,
                    content: message,
                    create_at_utc: new Date().toISOString(),
                },
            ]);
        }

        sendMessage(message);
    };

    const handleSetPrompt = useCallback(
        (newPrompt: ChatPromptType) => {
            return new Promise<void>((resolve) => {
                setCurrentPrompt(newPrompt);
                handleSetup().then(() => {
                    resolve();
                });
            });
        },
        [handleSetup]
    );

    if (!sessionId || !localUser || !instructorId) {
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
                instructorId,
                messages,
                pendingTools: pendingToolNames,
                toolResults,
                isProcessing,
                sendMessage: handleSendMessage,
                setInstructor: setInstructorId,
                setPrompt: handleSetPrompt,
                reset: handleSetup,
            }}
        >
            {children}
        </ChatContext.Provider>
    );
};
