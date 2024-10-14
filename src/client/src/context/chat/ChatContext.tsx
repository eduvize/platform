import { ChatMessageDto, CompletionChunkDto } from "@models/dto";
import { ChatPromptType } from "@models/enums";
import { ReactNode, useEffect, useState, useCallback, useRef } from "react";
import { createContext } from "use-context-selector";
import { useContext } from "react";
import { AudioOutputContext } from "../audio/AudioOutputContext";
import { useAudioInput } from "@context/audio/hooks";
import * as WavEncoder from "wav-encoder";
import io, { Socket } from "socket.io-client";
const socketEndpoint = import.meta.env.VITE_SOCKETIO_ENDPOINT;

// Types and Interfaces
type Context = {
    instructorId: string | null;
    messages: ChatMessageDto[];
    pendingTools: string[];
    toolResults: Record<string, any | null>;
    isProcessing: boolean;
    sendMessage: (message: string, hideFromChat?: boolean) => void;
    sendAudio: (audio: ArrayBuffer) => void;
    setInstructor: (instructorId: string) => Promise<void>;
    setPrompt: (prompt: ChatPromptType) => Promise<void>;
    reset: () => void;
};

interface ChatProviderProps {
    children: ReactNode;
}

// Default Context Value
const defaultValue: Context = {
    instructorId: null,
    messages: [],
    pendingTools: [],
    toolResults: {},
    isProcessing: false,
    sendMessage: () => {},
    sendAudio: () => {},
    setInstructor: () => Promise.resolve(),
    setPrompt: () => Promise.resolve(),
    reset: () => {},
};

export const ChatContext = createContext<Context>(defaultValue);

export const ChatProvider = ({ children }: ChatProviderProps) => {
    // State
    const [isConnected, setIsConnected] = useState(false);
    const [pendingToolNames, setPendingToolNames] = useState<string[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [toolResults, setToolResults] = useState<Record<string, any | null>>(
        {}
    );
    const [currentPrompt, setCurrentPrompt] = useState<ChatPromptType | null>(
        null
    );
    const [instructorId, setInstructorId] = useState<string | null>(null);
    const [messages, setMessages] = useState<ChatMessageDto[]>([]);

    // Refs
    const socketRef = useRef<Socket | null>(null);
    const sseCancellationHandlerRef = useRef<{ cancel: () => void }>({
        cancel: () => {},
    });

    // Get the playAudio function from AudioOutputContext
    const { playAudio, stopPlayback } = useContext(AudioOutputContext);
    const { isListening, sampleRate, isSpeaking } = useAudioInput();

    // Effects
    useEffect(() => {
        socketRef.current = io(`${socketEndpoint}/chat`, {
            forceNew: true,
            extraHeaders: {
                Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
        });

        socketRef.current.on("connect", () => {
            console.log("Connected to chat socket");

            setIsConnected(true);
        });

        socketRef.current.on(
            "message_update",
            (message: CompletionChunkDto) => {
                if (message.audio) {
                    playAudio(message.audio);
                }

                if (message.received_text) {
                    setMessages((prev) => [
                        ...prev,
                        {
                            id: `${Date.now()}`,
                            is_user: true,
                            content: message.received_text!,
                            create_at_utc: new Date().toISOString(),
                        },
                    ]);
                }

                if (message.text) {
                    setMessages((prev) => {
                        const lastMessage = prev[prev.length - 1];

                        if (
                            lastMessage &&
                            lastMessage.id === message.message_id
                        ) {
                            return [
                                ...prev.slice(0, -1),
                                {
                                    ...lastMessage,
                                    content:
                                        lastMessage.content +
                                        (message.text || ""),
                                },
                            ];
                        }

                        stopPlayback();

                        return [
                            ...prev,
                            {
                                id: message.message_id,
                                is_user: false,
                                content: message.text || "",
                                create_at_utc: new Date().toISOString(),
                            },
                        ];
                    });
                }
            }
        );

        socketRef.current.on("message_complete", () => {
            setIsProcessing(false);
        });

        socketRef.current.on("disconnect", () => {
            console.log("Disconnected from chat socket");
        });
    }, []);

    useEffect(() => {
        socketRef.current?.emit("use_voice", {
            enabled: isListening,
        });
    }, [isListening]);

    useEffect(() => {
        updateToolResults();
    }, [toolResults]);

    const sendMessage = (message: string) => {
        socketRef.current?.emit("send_message", {
            message,
        });
    };

    const sendAudio = (audio: string) => {
        socketRef.current?.emit("send_message", {
            audio,
        });
    };

    const handleSendMessage = useCallback(
        (message: string, hideFromChat?: boolean) => {
            if (isProcessing) return;

            setIsProcessing(true);

            if (!hideFromChat) {
                addUserMessage(message);
            }

            sendMessage(message);
        },
        [isProcessing, sendMessage]
    );

    const handleSendAudio = useCallback(
        (audio: ArrayBuffer) => {
            WavEncoder.encode({
                sampleRate,
                channelData: [new Float32Array(audio)],
            }).then((wavBuffer) => {
                // Convert ArrayBuffer to Base64 properly
                const uint8Array = new Uint8Array(wavBuffer);
                const base64 = btoa(
                    uint8Array.reduce(
                        (data, byte) => data + String.fromCharCode(byte),
                        ""
                    )
                );
                sendAudio(base64);
            });
        },
        [sendAudio, sampleRate]
    );

    const handleSetInstructor = (newInstructorId: string) => {
        console.log("Setting instructor to", newInstructorId);

        stopPlayback();

        return new Promise<void>((resolve) => {
            console.log("Setting instructor t43234234o", newInstructorId);
            socketRef.current?.emit("set_instructor", {
                instructor_id: newInstructorId,
            });

            setInstructorId(newInstructorId);

            resolve();
        });
    };

    const handleSetPrompt = (newPrompt: ChatPromptType) => {
        return new Promise<void>((resolve) => {
            socketRef.current?.emit("set_prompt", {
                prompt_type: newPrompt,
            });

            setCurrentPrompt(newPrompt);

            resolve();
        });
    };

    // Helper functions
    /**
     * Updates the tool results in the last message.
     */
    const updateToolResults = () => {
        setMessages((prev) => {
            if (prev.length === 0) return prev;

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
    };

    const handleToolCalls = (
        tools: any[],
        completedToolCalls: Record<string, any>
    ) => {
        setPendingToolNames((prev) => [
            ...prev,
            ...tools
                .map((tool) => tool.name)
                .filter((name) => !prev.includes(name)),
        ]);

        for (const tool of tools) {
            if (!completedToolCalls[tool.name]) {
                toolResults[tool.name] = null;
            }

            try {
                const data = JSON.parse(tool.data);
                completedToolCalls[tool.name] = data;
            } catch (e) {}
        }
    };

    /**
     * Adds a user message to the messages state.
     * @param message - The message content from the user.
     */
    const addUserMessage = (message: string) => {
        setMessages((prev) => [
            ...prev,
            {
                id: `${Date.now()}`,
                is_user: true,
                content: message,
                create_at_utc: new Date().toISOString(),
            },
        ]);
    };

    // Add an effect to watch for changes in isSpeaking
    useEffect(() => {
        if (isSpeaking) {
            console.log("Stopping playback");
            stopPlayback();
            sseCancellationHandlerRef.current.cancel?.();
        }
    }, [isSpeaking]);

    // Context value
    const contextValue: Context = {
        instructorId,
        messages,
        pendingTools: pendingToolNames,
        toolResults,
        isProcessing,
        sendMessage: handleSendMessage,
        sendAudio: handleSendAudio,
        setInstructor: handleSetInstructor,
        setPrompt: handleSetPrompt,
        reset: () => {
            stopPlayback();
            setMessages([]);
        },
    };

    return (
        <ChatContext.Provider value={contextValue}>
            {children}
        </ChatContext.Provider>
    );
};
