import { Bubble } from "@atoms";
import { Flex, Group, Stack } from "@mantine/core";
import Markdown from "react-markdown";
import { ChatMessageDto } from "@models/dto";
import classes from "./ChatMessage.module.css";

interface ChatMessageProps extends ChatMessageDto {}

export const ChatMessage = ({ is_user, content }: ChatMessageProps) => {
    let parts = [
        <Flex
            align="center"
            justify={is_user ? "flex-end" : "flex-start"}
            h="100%"
        >
            <Bubble bg={is_user ? "#1479B2" : "#5F3DC4"} p="6px" px="12px">
                <Markdown className={classes.message}>{content}</Markdown>
            </Bubble>
        </Flex>,
    ];

    if (is_user) {
        parts = parts.reverse();
    }

    return (
        <Stack>
            <Group justify={is_user ? "flex-end" : "flex-start"}>{parts}</Group>
        </Stack>
    );
};
