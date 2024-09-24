import { useMemo } from "react";
import { Bubble } from "@atoms";
import { useCurrentUser } from "@context/user/hooks";
import { Avatar, Flex, Grid, Group, Stack } from "@mantine/core";
import Markdown from "react-markdown";
import { ChatMessageDto } from "@models/dto";
import classes from "./ChatMessage.module.css";
import avatar from "./avatar.png";

interface ChatMessageProps extends ChatMessageDto {}

export const ChatMessage = ({ is_user, content }: ChatMessageProps) => {
    const [localUser] = useCurrentUser();
    const avatarUrl = is_user ? localUser?.profile.avatar_url : avatar;

    const initials = useMemo(() => {
        if (!is_user) return "";
        if (!localUser) return "";

        if (!localUser.profile.first_name || !localUser.profile.last_name) {
            return localUser.username[0];
        }
        return `${localUser.profile.first_name![0]}${
            localUser.profile.last_name![0]
        }`;
    }, [localUser]);

    let parts = [
        <Grid.Col span={0.8}>
            <Group justify={is_user ? "flex-end" : "flex-start"}>
                <Avatar radius="50%" size="md" src={avatarUrl}>
                    {initials}
                </Avatar>
            </Group>
        </Grid.Col>,
        <Grid.Col span="auto">
            <Flex
                align="center"
                justify={is_user ? "flex-end" : "flex-start"}
                h="100%"
            >
                <Bubble
                    tipSide={is_user ? "right" : "left"}
                    bg={is_user ? "blue" : "gray"}
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
