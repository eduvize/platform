import { useChatMessages } from "@context/chat/hooks";
import { Input, ScrollArea, Stack } from "@mantine/core";
import { ChatMessage } from "@molecules";
import { useEffect, useRef, useState } from "react";

interface ChatProps {
    height: string;
}

export const Chat = ({ height }: ChatProps) => {
    const viewport = useRef<HTMLDivElement>(null);
    const [messages, sendMessage] = useChatMessages();
    const [message, setMessage] = useState("");

    const handleScrollToBottom = () => {
        viewport.current?.scrollTo({
            top: viewport.current.scrollHeight,
            behavior: "smooth",
        });
    };

    useEffect(() => {
        handleScrollToBottom();
    }, [messages]);

    return (
        <Stack gap={0}>
            <ScrollArea.Autosize
                viewportRef={viewport}
                h={height}
                scrollbars="y"
            >
                <Stack gap="xl">
                    {messages.map((message) => (
                        <ChatMessage {...message} />
                    ))}
                </Stack>
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
            />
        </Stack>
    );
};
