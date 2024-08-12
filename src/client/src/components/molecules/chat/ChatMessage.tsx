import { Bubble } from "@atoms";
import { useChatAvatar } from "@context/chat/hooks";
import { useCurrentUser } from "@context/user/hooks";
import { Avatar, Flex, Grid, Stack, Text } from "@mantine/core";
import { ChatMessageDto } from "@models/dto";
import { useMemo } from "react";

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

    const textHtml = useMemo(() => {
        let msg = content.replace(/\n/g, "<br />");

        // Markdown bolding
        msg = msg.replace(/\*\*(.*?)\*\*/g, "<b>$1</b>");

        // Markdown italics
        msg = msg.replace(/\*(.*?)\*/g, "<i>$1</i>");

        // Markdown code
        msg = msg.replace(/`(.*?)`/g, "<code>$1</code>");

        // Markdown links
        msg = msg.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>');

        // Markdown lists
        msg = msg.replace(/^\s*-\s*(.*)$/gm, "<li>$1</li>");

        // Markdown headings
        msg = msg.replace(/^# (.*?)$/gm, "<h1>$1</h1>");
        msg = msg.replace(/^## (.*?)$/gm, "<h2>$1</h2>");
        msg = msg.replace(/^### (.*?)$/gm, "<h3>$1</h3>");
        msg = msg.replace(/^#### (.*?)$/gm, "<h4>$1</h4>");
        msg = msg.replace(/^##### (.*?)$/gm, "<h5>$1</h5>");

        return msg;
    }, [content]);

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
                    ml={is_user ? undefined : "lg"}
                    mr={is_user ? "sm" : undefined}
                >
                    <Text
                        dangerouslySetInnerHTML={{ __html: textHtml }}
                        size="sm"
                        c={is_user ? "white" : undefined}
                    ></Text>
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
