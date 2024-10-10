import { useEffect, useRef, useState, forwardRef } from "react";
import { ChatMessage, PendingTool } from "@molecules";
import { useChat, usePendingTools, useToolResults } from "@context/chat/hooks";
import {
    Box,
    Card,
    Divider,
    Flex,
    Input,
    ScrollArea,
    Stack,
    Text,
} from "@mantine/core";
import { InstructorAvatar } from "@atoms";

interface ChatProps {
    maxHeight?: number | string;
    greetingMessage?: string;
    toolDescriptionMap?: Record<string, string>;
    onTool?: (name: string, data: any) => void;
    onMessageData?: () => void;
}

const AVATAR_SIZE = 84;

/**
 * The chat component is a top-level component that directly ties into the chat context to handle the sending, receiving and display of messages
 * in a common format. Tools are handled by consumers of the chat component, where the toolDescriptionMap is used to provide
 * a user-friendly description of the tool being processed, and onTool is used to handle the results of tools.
 */
export const Chat = forwardRef<HTMLDivElement, ChatProps>(
    (
        {
            maxHeight,
            greetingMessage,
            toolDescriptionMap,
            onTool,
            onMessageData,
        },
        chatAreaRef
    ) => {
        const viewport = useRef<HTMLDivElement>(null);
        const isAtBottomRef = useRef(true);
        const pendingToolNames = usePendingTools();
        const toolResults = useToolResults();
        const { messages, sendMessage, processing } = useChat(greetingMessage);
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

            if (
                (greetingMessage && messages.length > 1) ||
                messages.length > 2
            ) {
                onMessageData?.();
            }
        }, [messages.map((x) => x.content)]);

        useEffect(() => {
            if (!toolResults) return;

            for (const [name, data] of Object.entries(toolResults)) {
                onTool?.(name, data);
            }
        }, [toolResults]);

        return (
            <Box pos="relative">
                <Box
                    pos="absolute"
                    top={-(AVATAR_SIZE / 4)}
                    left="50%"
                    ml={-(AVATAR_SIZE / 2)}
                    style={{ zIndex: 2 }}
                >
                    <InstructorAvatar size={AVATAR_SIZE} />
                </Box>

                <Card
                    withBorder
                    ref={chatAreaRef}
                    pos="relative"
                    w="100%"
                    p={0}
                    bg="#2D262B"
                >
                    <Flex
                        bg="#242424"
                        justify="center"
                        py="xs"
                        px="sm"
                        direction="column"
                    >
                        <Stack gap={0}>
                            <Text size="xs" lh={1}>
                                Chatting with:
                            </Text>
                            <Text size="md" c="white" lh={1}>
                                Kyle
                            </Text>
                        </Stack>
                    </Flex>

                    <Flex pos="relative" direction="column" w="100%" p="md">
                        <ScrollArea.Autosize
                            display="flex"
                            flex="1 0 auto"
                            h={maxHeight}
                            viewportRef={viewport}
                            pr={0}
                            pt="xl"
                            scrollbars="y"
                            onScroll={() => {
                                isAtBottomRef.current =
                                    viewport.current!.scrollTop +
                                        viewport.current!.clientHeight >=
                                    viewport.current!.scrollHeight;
                            }}
                            style={{
                                transition: "height 0.2s",
                            }}
                        >
                            <Stack
                                gap="md"
                                pb={pendingToolNames.length ? "xl" : undefined}
                                pr="sm"
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
                                                toolDescriptionMap?.[
                                                    toolName
                                                ] ?? "Working some magic..."
                                            }
                                        />
                                    ))}
                                </Box>
                            )}
                        </ScrollArea.Autosize>

                        <Divider />

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
                            styles={{
                                input: {
                                    backgroundColor: "#424242",
                                    color: "#828282",
                                },
                            }}
                        />
                    </Flex>
                </Card>
            </Box>
        );
    }
);
