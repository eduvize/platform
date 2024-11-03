import { ChatMessageDto, CompletionChunkDto } from "@models/dto";
import { ChatPromptType } from "@models/enums";
import { ReactNode, useEffect, useState, useCallback, useRef } from "react";
import { createContext } from "use-context-selector";
import { useContext } from "react";
import { AudioOutputContext } from "../audio/AudioOutputContext";
import { useAudioInput, useIncomingAudioEffect } from "@context/audio/hooks";
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
    data: Record<string, any>;
    setData: (data: Record<string, any>) => void;
    sendMessage: (
        message: string,
        hideFromChat?: boolean,
        data?: Record<string, any>
    ) => void;
    sendAudio: (audio: ArrayBuffer) => void;
    setInstructor: (instructorId: string) => Promise<void>;
    setPrompt: (prompt: ChatPromptType) => Promise<void>;
    setLessonId: (lessonId: string) => Promise<void>;
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
    data: {},
    setData: () => {},
    sendMessage: () => {},
    sendAudio: () => {},
    setInstructor: () => Promise.resolve(),
    setPrompt: () => Promise.resolve(),
    setLessonId: () => Promise.resolve(),
    reset: () => {},
};

export const ChatContext = createContext<Context>(defaultValue);

// Add this at the top of the file, outside of any component
let globalSocket: Socket | null = null;
const getSocket = () => {
    if (!globalSocket) {
        globalSocket = io(`${socketEndpoint}/chat`, {
            forceNew: true,
            extraHeaders: {
                Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
        });
    }
    return globalSocket;
};

export const ChatProvider = ({ children }: ChatProviderProps) => {
    // State
    const [isConnected, setIsConnected] = useState(false);
    const [pendingToolNames, setPendingToolNames] = useState<string[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [finalToolResults, setFinalToolResults] = useState<
        Record<string, any | null>
    >({});
    const [currentPrompt, setCurrentPrompt] = useState<ChatPromptType | null>(
        null
    );
    const [data, setData] = useState<Record<string, any>>({});
    const [instructorId, setInstructorId] = useState<string | null>(null);
    const [messages, setMessages] = useState<ChatMessageDto[]>([]);
    const messageCompleteRef = useRef(false);

    // Refs
    const sseCancellationHandlerRef = useRef<{ cancel: () => void }>({
        cancel: () => {},
    });
    const liveTranscriptionRef = useRef<string | null>(null);
    const instructorIdRef = useRef<string | null>(null);
    const currentPromptRef = useRef<ChatPromptType | null>(null);

    // Add a ref to track if we've initialized
    const hasInitialized = useRef(false);

    // Get the playAudio function from AudioOutputContext
    const { playAudio, stopPlayback, enablePlayback, disablePlayback } =
        useContext(AudioOutputContext);
    const { isListening, sampleRate, isSpeaking } = useAudioInput();

    // Effects
    useEffect(() => {
        // Prevent multiple initializations
        if (hasInitialized.current) return;
        hasInitialized.current = true;

        const socket = getSocket();

        socket.on("connect", () => {
            console.log("Connected to chat socket");

            setIsConnected(true);
        });

        socket.on("message_update", (message: CompletionChunkDto) => {
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
                    const lastMessage = prev.filter(
                        (x) => x.id != "live_transcription"
                    )[prev.length - 1];

                    if (
                        lastMessage &&
                        !lastMessage.is_user &&
                        lastMessage.id === message.message_id
                    ) {
                        return prev.map((prevMsg, index) => {
                            if (prevMsg.id === lastMessage.id) {
                                return {
                                    ...prevMsg,
                                    content:
                                        prevMsg.content + message.text || "",
                                };
                            }

                            return prevMsg;
                        });
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

            if (message.tools && message.tools.length > 0) {
                const jsonCompleteTools = message.tools.filter((t) => {
                    try {
                        JSON.parse(t.data);
                        return true;
                    } catch (e) {
                        return false;
                    }
                });

                setFinalToolResults((prev) => ({
                    ...prev,
                    ...jsonCompleteTools.reduce(
                        (acc, tool) => ({
                            ...acc,
                            [tool.name]: tool.data,
                        }),
                        {}
                    ),
                }));
            }
        });

        socket.on("message_complete", () => {
            setIsProcessing(false);
        });

        socket.on(
            "continue_session",
            (data: { session_id: string; instructor_id?: string }) => {
                console.log("Continuing session", data);

                if (data.instructor_id) {
                    setInstructorId(data.instructor_id);
                }
            }
        );

        socket.on(
            "start_session",
            (data: { session_id: string; instructor_id?: string }) => {
                console.log("Starting session", data);

                if (data.instructor_id) {
                    setInstructorId(data.instructor_id);
                }
            }
        );

        socket.on("purge_session", () => {
            console.log("Purging session");
            setMessages([]);
        });

        socket.on("voice_transcript", (transcript: string) => {
            console.log("Voice transcript:", transcript);
            liveTranscriptionRef.current = transcript;

            stopPlayback();

            setMessages((prev) => {
                if (!prev.some((x) => x.id == "live_transcription")) {
                    return [
                        ...prev,
                        {
                            id: "live_transcription",
                            is_user: true,
                            content: transcript,
                            create_at_utc: new Date().toISOString(),
                        },
                    ];
                } else {
                    return prev.map((x) => {
                        if (x.id == "live_transcription") {
                            return {
                                ...x,
                                content: transcript,
                            };
                        }

                        return x;
                    });
                }
            });
        });

        socket.on("voice_end", () => {
            if (liveTranscriptionRef.current) {
                handleSendMessage(liveTranscriptionRef.current);
            }

            liveTranscriptionRef.current = null;
            setMessages((prev) => {
                if (prev.some((x) => x.id == "live_transcription")) {
                    return prev.filter((x) => x.id != "live_transcription");
                }

                return prev;
            });
        });

        socket.on("disconnect", () => {
            console.log("Disconnected from chat socket");
        });

        // Cleanup function - don't disconnect, just remove listeners
        return () => {
            socket.removeAllListeners();
        };
    }, []); // Empty dependency array

    useIncomingAudioEffect((data) => {
        getSocket()?.emit("audio_data", data);
    });

    useEffect(() => {
        if (sampleRate) {
            getSocket()?.emit("use_voice", {
                enabled: isListening,
                sample_rate: sampleRate,
            });

            if (isListening) {
                enablePlayback();
            } else {
                disablePlayback();
                stopPlayback();
            }
        }
    }, [isListening, sampleRate]);

    useEffect(() => {
        if (!isProcessing && Object.keys(finalToolResults).length > 0) {
            setFinalToolResults({});
        }
    }, [isProcessing]);

    const sendMessage = (message: string, hideFromChat?: boolean) => {
        getSocket()?.emit("send_message", {
            prompt: currentPromptRef.current,
            message,
            hide_from_chat: hideFromChat,
            data: data || {},
        });
    };

    const sendAudio = (audio: string) => {
        getSocket()?.emit("send_message", { audio });
    };

    const handleSendMessage = useCallback(
        (message: string, hideFromChat?: boolean) => {
            if (isProcessing) return;

            setIsProcessing(true);

            if (!hideFromChat) {
                addUserMessage(message);
            }

            sendMessage(message, hideFromChat);
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

        return new Promise<void>((resolve) => {
            if (newInstructorId === instructorIdRef.current) return;
            stopPlayback();

            getSocket()?.emit("set_instructor", {
                instructor_id: newInstructorId,
            });

            getSocket()?.once("instructor_set", () => {
                instructorIdRef.current = newInstructorId;
                setInstructorId(newInstructorId);
                resolve();
            });
        });
    };

    const handleSetPrompt = (newPrompt: ChatPromptType) => {
        return new Promise<void>((resolve) => {
            if (newPrompt === currentPromptRef.current) return;

            getSocket()?.emit("set_prompt", {
                prompt_type: newPrompt,
            });

            stopPlayback();

            getSocket()?.once("prompt_set", () => {
                currentPromptRef.current = newPrompt;
                setCurrentPrompt(newPrompt);
                resolve();
            });
        });
    };

    const handleSetLessonId = (
        lessonId: string,
        section?: number
    ): Promise<void> => {
        return new Promise<void>((resolve) => {
            getSocket()?.emit("create_lesson_session", {
                lesson_id: lessonId,
                section,
            });

            getSocket()?.once("lesson_id_set", () => {
                resolve();
            });
        });
    };

    // Helper functions

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
        toolResults: finalToolResults,
        isProcessing,
        sendMessage: handleSendMessage,
        sendAudio: handleSendAudio,
        setInstructor: handleSetInstructor,
        setPrompt: handleSetPrompt,
        setLessonId: handleSetLessonId,
        data,
        setData,
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

// Add this cleanup function to be called when you want to completely disconnect
// (e.g., on logout or tab close)
export const cleanupChatSocket = () => {
    if (globalSocket) {
        globalSocket.disconnect();
        globalSocket = null;
    }
};
