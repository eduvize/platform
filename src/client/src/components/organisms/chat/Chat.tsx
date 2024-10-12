import {
    useEffect,
    useRef,
    useState,
    forwardRef,
    useCallback,
    useMemo,
} from "react";
import { ChatMessage, PendingTool } from "@molecules";
import { useChat, usePendingTools, useToolResults } from "@context/chat/hooks";
import {
    Box,
    Card,
    Divider,
    Flex,
    Input,
    ScrollArea,
    Space,
    Stack,
    Text,
} from "@mantine/core";
import { InstructorAvatar } from "@atoms";
import { useInstructors } from "@hooks/instructors";

interface ChatProps {
    maxHeight?: number | string;
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
    ({ maxHeight, toolDescriptionMap, onTool, onMessageData }, chatAreaRef) => {
        const instructors = useInstructors();
        const pendingToolNames = usePendingTools();
        const toolResults = useToolResults();
        const { messages, sendMessage, processing, instructorId } = useChat();
        const inputRef = useRef<HTMLInputElement>(null);
        const scrollRef = useRef<HTMLDivElement>(null);
        const viewport = useRef<HTMLDivElement>(null);
        const [message, setMessage] = useState("");
        const [isAtBottom, setIsAtBottom] = useState(true);
        const [userHasScrolled, setUserHasScrolled] = useState(false);

        const instructor = useMemo(() => {
            return instructors.find((x) => x.id === instructorId);
        }, [instructors, instructorId]);

        const scrollToBottom = useCallback(() => {
            if (viewport.current) {
                viewport.current.scrollTop = viewport.current.scrollHeight;
            }
        }, []);

        const checkIfAtBottom = useCallback(() => {
            if (viewport.current) {
                const { scrollTop, scrollHeight, clientHeight } =
                    viewport.current;
                return Math.abs(scrollHeight - clientHeight - scrollTop) < 1;
            }
            return false;
        }, []);

        useEffect(() => {
            if (isAtBottom && !userHasScrolled) {
                scrollToBottom();
            }
        }, [
            messages,
            pendingToolNames,
            isAtBottom,
            userHasScrolled,
            scrollToBottom,
        ]);

        // Effect to re-focus input when processing is complete
        useEffect(() => {
            if (!processing && inputRef.current) {
                inputRef.current.focus();
            }
        }, [processing]);

        useEffect(() => {
            scrollToBottom();

            if (messages.length > 1 || messages.length > 2) {
                onMessageData?.();
            }
        }, [messages.map((x) => x.content)]);

        useEffect(() => {
            if (!toolResults) return;

            for (const [name, data] of Object.entries(toolResults)) {
                onTool?.(name, data);
            }
        }, [toolResults]);

        useEffect(() => {
            if (isAtBottom) {
                scrollToBottom();
            }
        }, [messages, pendingToolNames]);

        // Split messages into multiple messages if newlines are encountered
        const splitMessages = useMemo(() => {
            return messages.flatMap((message) => {
                const contentChunks = message.content.split("\n");
                return contentChunks
                    .filter((chunk) => chunk.trim() !== "") // Filter out blank messages
                    .map((chunk) => ({
                        ...message,
                        content: chunk.trim(), // Trim any leading/trailing whitespace
                    }));
            });
        }, [messages]);

        return (
            <Box pos="relative">
                <Box
                    pos="absolute"
                    top={-(AVATAR_SIZE / 4)}
                    left="50%"
                    ml={-(AVATAR_SIZE / 2)}
                    style={{ zIndex: 2 }}
                >
                    <InstructorAvatar id={instructorId} size={AVATAR_SIZE} />
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
                                {instructor?.name}
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
                            onScrollPositionChange={() => {
                                const atBottom = checkIfAtBottom();
                                setIsAtBottom(atBottom);
                                if (!atBottom && !userHasScrolled) {
                                    setUserHasScrolled(true);
                                }
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
                                {splitMessages.map((message, index) => (
                                    <ChatMessage
                                        key={`${message.create_at_utc}-${index}`}
                                        {...message}
                                    />
                                ))}
                            </Stack>

                            {pendingToolNames.length > 0 && (
                                <Box mt="md" pos="absolute" bottom="0" left="0">
                                    {pendingToolNames.map((toolName) => (
                                        <PendingTool
                                            key={toolName}
                                            name={
                                                toolDescriptionMap?.[
                                                    toolName
                                                ] ?? "Working some magic..."
                                            }
                                        />
                                    ))}
                                </Box>
                            )}

                            <Space h="xl" />
                            <div ref={scrollRef} />
                        </ScrollArea.Autosize>

                        <Divider />

                        <Input
                            ref={inputRef}
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
                                    setUserHasScrolled(false);
                                    setIsAtBottom(true);
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
