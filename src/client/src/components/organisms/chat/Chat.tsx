import { useEffect, useRef, useState } from "react";
import { ChatMessage, PendingTool } from "@molecules";
import {
    useChatMessages,
    usePendingTools,
    useToolResults,
} from "@context/chat/hooks";
import { Box, Input, ScrollArea, Stack } from "@mantine/core";

interface ChatProps {
    height: string;
    toolDescriptionMap?: Record<string, string>;
    onTool?: (name: string, data: any) => void;
}

/**
 * The chat component is a top-level component that directly ties into the chat context to handle the sending, receiving and display of messages
 * in a common format. Tools are handled by consumers of the chat component, where the toolDescriptionMap is used to provide
 * a user-friendly description of the tool being processed, and onTool is used to handle the results of tools.
 */
export const Chat = ({ height, toolDescriptionMap, onTool }: ChatProps) => {
    const viewport = useRef<HTMLDivElement>(null);
    const isAtBottomRef = useRef(true);
    const pendingToolNames = usePendingTools();
    const toolResults = useToolResults();
    const { messages, sendMessage, processing } = useChatMessages();
    const [message, setMessage] = useState("");

    const handleScrollToBottom = () => {
        viewport.current?.scrollTo({
            top: viewport.current.scrollHeight,
            behavior: "smooth",
        });
    };

    useEffect(() => {
        handleScrollToBottom();
    }, [pendingToolNames.length, messages.length]);

    useEffect(() => {
        if (isAtBottomRef.current) {
            handleScrollToBottom();
        }
    }, [messages.map((x) => x.content)]);

    useEffect(() => {
        if (!toolResults) return;

        for (const [name, data] of Object.entries(toolResults)) {
            onTool?.(name, data);
        }
    }, [toolResults]);

    return (
        <Stack gap={0}>
            <ScrollArea.Autosize
                viewportRef={viewport}
                h={height}
                p="lg"
                scrollbars="y"
                onScroll={() => {
                    isAtBottomRef.current =
                        viewport.current!.scrollTop +
                            viewport.current!.clientHeight >=
                        viewport.current!.scrollHeight;
                }}
            >
                <Stack
                    gap="xl"
                    mt="md"
                    pb={pendingToolNames.length ? "xl" : undefined}
                >
                    {messages.map((message) => (
                        <ChatMessage {...message} />
                    ))}
                </Stack>

                {pendingToolNames.length > 0 && (
                    <Box mt="md" pos="absolute" bottom="0" left="0">
                        {pendingToolNames.map((toolName) => (
                            <PendingTool
                                name={
                                    toolDescriptionMap?.[toolName] ??
                                    "Working some magic..."
                                }
                            />
                        ))}
                    </Box>
                )}
            </ScrollArea.Autosize>

            <Input
                mt="md"
                placeholder="Type a message..."
                variant="filled"
                radius="xl"
                value={message}
                onChange={(e) => setMessage(e.currentTarget.value)}
                onKeyDown={(e) => {
                    if (e.key === "Enter") {
                        sendMessage(message);
                        setMessage("");
                    }
                }}
                disabled={processing}
            />
        </Stack>
    );
};
