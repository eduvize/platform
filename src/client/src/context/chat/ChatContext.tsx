import { ChatApi } from "@api";
import { ChatMessageDto, CompletionChunkDto } from "@models/dto";
import { ChatPromptType } from "@models/enums";
import { ReactNode, useEffect, useState, useCallback, useRef } from "react";
import { createContext } from "use-context-selector";
import { useContext } from "react";
import { AudioOutputContext } from "../audio/AudioOutputContext";
import { useAudioInput } from "@context/audio/hooks";
import * as WavEncoder from "wav-encoder";

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
    const [pendingToolNames, setPendingToolNames] = useState<string[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [toolResults, setToolResults] = useState<Record<string, any | null>>(
        {}
    );
    const [currentPrompt, setCurrentPrompt] = useState<ChatPromptType | null>(
        null
    );
    const [instructorId, setInstructorId] = useState<string | null>(null);
    const [receiveBuffer, setReceiveBuffer] = useState<string>("");
    const [messages, setMessages] = useState<ChatMessageDto[]>([]);

    // Refs
    const sessionIdRef = useRef<string | null>(null);
    const instructorIdRef = useRef<string | null>(null);
    const promptRef = useRef<ChatPromptType | null>(null);
    const incomingMessageCompleteRef = useRef(true);
    const cachedInstructorIdRef = useRef<string | null>(null);
    const cachedPromptRef = useRef<ChatPromptType | null>(null);
    const streamingMessageIdRef = useRef<string | null>(null);
    const shouldDiscardIncomingDataRef = useRef<boolean>(false);
    const sseCancellationHandlerRef = useRef<{ cancel: () => void }>({
        cancel: () => {},
    });

    // Get the playAudio function from AudioOutputContext
    const { playAudio, stopPlayback } = useContext(AudioOutputContext);
    const { isListening, sampleRate, isSpeaking } = useAudioInput();

    // Effects
    useEffect(() => {
        if (receiveBuffer === "") return;
        updateMessages();
    }, [receiveBuffer, messages]);

    useEffect(() => {
        updateToolResults();
    }, [toolResults]);

    // Callbacks
    const handleSetup = async () => {
        if (!instructorIdRef.current || !promptRef.current) return;

        stopPlayback();
        sseCancellationHandlerRef.current.cancel?.();

        const { id: session_id, instructor_id } = await ChatApi.createSession(
            promptRef.current,
            instructorIdRef.current ?? undefined
        );
        sessionIdRef.current = session_id;
        incomingMessageCompleteRef.current = true;
        setInstructorId(instructor_id);
        setMessages([]);
        cachedPromptRef.current = currentPrompt;
        cachedInstructorIdRef.current = instructor_id;
    };

    useEffect(() => {
        handleSetup();
    }, []);

    const sendMessage = (message: string) => {
        if (!sessionIdRef.current || !incomingMessageCompleteRef.current) {
            console.error(
                "Session ID or incoming message complete flag not set"
            );
            return;
        }

        let receivedText = "";
        let completedToolCalls: Record<string, any> = {};

        const { cancel } = ChatApi.sendMessage(
            sessionIdRef.current,
            { message, expect_audio_response: isListening },
            handleChunk(receivedText, completedToolCalls),
            handleComplete(completedToolCalls)
        );

        sseCancellationHandlerRef.current.cancel = cancel;
    };

    const sendAudio = (audio: string) => {
        if (!sessionIdRef.current) {
            return;
        }

        let receivedText = "";
        let completedToolCalls: Record<string, any> = {};

        const { cancel } = ChatApi.sendMessage(
            sessionIdRef.current,
            { audio, expect_audio_response: isListening },
            handleChunk(receivedText, completedToolCalls),
            handleComplete(completedToolCalls)
        );

        sseCancellationHandlerRef.current.cancel = cancel;
    };

    const handleSendMessage = useCallback(
        (message: string, hideFromChat?: boolean) => {
            if (isProcessing || !sessionIdRef.current) return;

            setIsProcessing(true);

            if (!hideFromChat) {
                addUserMessage(message);
            }

            sendMessage(message);
            incomingMessageCompleteRef.current = false;
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

    const handleSetPrompt = useCallback(
        (newPrompt: ChatPromptType) => {
            promptRef.current = newPrompt;

            return new Promise<void>((resolve) => {
                if (newPrompt !== cachedPromptRef.current) {
                    setCurrentPrompt(newPrompt);
                    handleSetup().then(resolve);
                } else {
                    resolve();
                }
            });
        },
        [handleSetup]
    );

    const handleSetInstructor = useCallback(
        (newInstructorId: string) => {
            instructorIdRef.current = newInstructorId;

            return handleSetup();
        },
        [handleSetup]
    );

    // Helper functions
    /**
     * Updates the messages state by either appending a new AI message or updating the last AI message.
     * Ensures that messages are not overwritten unintentionally and prevents duplicate messages.
     */
    const updateMessages = () => {
        setMessages((prevMessages) => {
            const lastMessage = prevMessages[prevMessages.length - 1];

            // Determine if the last message is an AI message that is still being updated
            if (
                lastMessage &&
                lastMessage.id === streamingMessageIdRef.current &&
                !lastMessage.is_user
            ) {
                // Update the existing AI message
                const updatedLastMessage: ChatMessageDto = {
                    ...lastMessage,
                    content: receiveBuffer,
                };
                return [...prevMessages.slice(0, -1), updatedLastMessage];
            } else if (streamingMessageIdRef.current) {
                // Append a new AI message only if we have a valid message ID
                const newMessage: ChatMessageDto = {
                    id: streamingMessageIdRef.current,
                    is_user: false,
                    content: receiveBuffer,
                    create_at_utc: new Date().toISOString(),
                };
                return [...prevMessages, newMessage];
            }

            // If no conditions are met, return the previous messages unchanged
            return prevMessages;
        });

        // Reset the receive buffer after updating
        setReceiveBuffer("");
    };

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

    const handleChunk =
        (receivedText: string, completedToolCalls: Record<string, any>) =>
        (chunk: CompletionChunkDto) => {
            // Check if we should discard incoming data
            if (shouldDiscardIncomingDataRef.current) {
                return; // Discard this chunk
            }

            streamingMessageIdRef.current = chunk.message_id;

            if (chunk.text) {
                receivedText += chunk.text;
                setReceiveBuffer(receivedText);
            }

            if (chunk.tools) {
                handleToolCalls(chunk.tools, completedToolCalls);
            }

            // Handle audio data using AudioOutputContext, but only if not discarding
            if (
                chunk.audio &&
                isListening &&
                !shouldDiscardIncomingDataRef.current
            ) {
                playAudio(chunk.audio);
            }

            if (chunk.received_text) {
                setMessages((prev) => [
                    ...prev,
                    {
                        id: `${Date.now()}`,
                        is_user: true,
                        content: chunk.received_text as string,
                        create_at_utc: new Date().toISOString(),
                    },
                ]);
            }
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

    const handleComplete = (completedToolCalls: Record<string, any>) => () => {
        incomingMessageCompleteRef.current = true;
        setPendingToolNames([]);
        setToolResults(completedToolCalls);
        setIsProcessing(false);
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
        shouldDiscardIncomingDataRef.current = isSpeaking;

        if (isSpeaking) {
            console.log("Stopping playback");
            incomingMessageCompleteRef.current = true;
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
        reset: handleSetup,
    };

    return (
        <ChatContext.Provider value={contextValue}>
            {children}
        </ChatContext.Provider>
    );
};
