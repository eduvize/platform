import { useMemo } from "react";
import { Bubble } from "@atoms";
import { useChatAvatar } from "@context/chat/hooks";
import { useCurrentUser } from "@context/user/hooks";
import { Avatar, Flex, Grid, Stack, Text } from "@mantine/core";
import Markdown from "react-markdown";
import { ChatMessageDto } from "@models/dto";
import classes from "./ChatMessage.module.css";

interface ChatMessageProps extends ChatMessageDto {}

export const ChatMessage = ({ is_user, content }: ChatMessageProps) => {
    const [localUser] = useCurrentUser();
    const avatarUrl = useChatAvatar(is_user ? "local" : "remote");

    const initials = useMemo(() => {
        if (!is_user) return "";
        if (!localUser) return "";

        return `${localUser.profile.first_name![0]}${
            localUser.profile.last_name![0]
        }`;
    }, [localUser]);

    let parts = [
        <Grid.Col span={1}>
            <Avatar radius="50%" size="lg" src={avatarUrl}>
                {initials}
            </Avatar>
        </Grid.Col>,
        <Grid.Col span={10}>
            <Flex
                align="center"
                justify={is_user ? "flex-end" : "flex-start"}
                h="100%"
            >
                <Bubble
                    tipSide={is_user ? "right" : "left"}
                    bg={is_user ? "blue" : "gray"}
                    mr={is_user ? "sm" : undefined}
                >
                    <Markdown className={classes.message}>{content}</Markdown>
                </Bubble>
            </Flex>
        </Grid.Col>,
    ];

    if (is_user) {
        parts = parts.reverse();
    }

    return (
        <Stack>
            <Grid>{parts}</Grid>
        </Stack>
    );
};
