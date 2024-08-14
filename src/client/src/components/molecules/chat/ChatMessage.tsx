import { Bubble } from "@atoms";
import { useChatAvatar } from "@context/chat/hooks";
import { useCurrentUser } from "@context/user/hooks";
import { Avatar, Flex, Grid, Stack, Text } from "@mantine/core";
import { ChatMessageDto } from "@models/dto";
import { useMemo } from "react";
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

    const textHtml = useMemo(() => {
        let msg = content
            .replace(/\n\s*\n/g, "\n") // Replace multiple newlines with a single newline
            .replace(/```([^`]+)```/g, "<pre><code>$1</code></pre>") // Multiline code blocks
            .replace(/`(.*?)`/g, "<code>$1</code>") // Inline code
            .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>") // Bold text
            .replace(/\*(.*?)\*/g, "<i>$1</i>") // Italic text
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>') // Links
            .replace(/^\d+\.\s+(.*)$/gm, "<li>$1</li>") // Ordered list items
            .replace(/(<li>.*<\/li>)/gm, "<ol>$1</ol>") // Wrap ordered list items in <ol>
            .replace(/^\s*-\s+(.*)$/gm, "<li>$1</li>") // Unordered list items
            .replace(/(<li>.*<\/li>)/gm, "<ul>$1</ul>") // Wrap unordered list items in <ul>
            .replace(/###### (.*?)$/gm, "<h6>$1</h6>") // Headings
            .replace(/##### (.*?)$/gm, "<h5>$1</h5>")
            .replace(/#### (.*?)$/gm, "<h4>$1</h4>")
            .replace(/### (.*?)$/gm, "<h3>$1</h3>")
            .replace(/## (.*?)$/gm, "<h2>$1</h2>")
            .replace(/# (.*?)$/gm, "<h1>$1</h1>")
            .replace(/^> (.*?)$/gm, "<blockquote>$1</blockquote>") // Blockquotes
            .replace(/---/g, "<hr />") // Horizontal rules
            .replace(/\n/g, "<br />"); // Line breaks

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
                        className={classes.message}
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
