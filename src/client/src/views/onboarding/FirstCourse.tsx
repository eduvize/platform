import { useToolCallEffect } from "@context/chat";
import {
    Stack,
    Title,
    Text,
    Space,
    Divider,
    Group,
    Button,
    Box,
    List,
} from "@mantine/core";
import { ChatTool } from "@models/enums";
import { useMemo, useState } from "react";

export const FirstCourse = () => {
    const [courseTitle, setCourseTitle] = useState<string>("");
    const [courseDescription, setCourseDescription] = useState<string>("");
    const [keyOutcomes, setKeyOutcomes] = useState<string[]>([]);
    const [topics, setTopics] = useState<string[]>([]);

    const shouldDisplayCourseInfo = useMemo(() => {
        return courseTitle.length > 0 && courseDescription.length > 0;
    }, [courseTitle, courseDescription]);

    useToolCallEffect(ChatTool.CourseBuilderSetCourseTitle, (result) => {
        setCourseTitle(result.title);
    });

    useToolCallEffect(ChatTool.CourseBuilderSetCourseDescription, (result) => {
        setCourseDescription(result.description);
    });

    useToolCallEffect(ChatTool.CourseBuilderSetCourseKeyOutcomes, (result) => {
        setKeyOutcomes(result.outcomes);
    });

    useToolCallEffect(ChatTool.CourseBuilderSetCourseTopics, (result) => {
        setTopics(result.topics);
    });

    return (
        <Stack pt="lg" gap="lg">
            <Title order={2} fw={400} c="white">
                Your First Course
            </Title>

            <Text>
                To build a Couse, simply start talking to your instructor about
                what you want to learn. You’ll be able to watch the general
                details of the course being built so that you can make any
                corrections before we build the whole course for you.
            </Text>

            <Box bg="dark">
                {!shouldDisplayCourseInfo && (
                    <Text ta="center" p="xl">
                        Your course summary will be displayed here
                    </Text>
                )}

                {shouldDisplayCourseInfo && (
                    <Stack p="lg">
                        <Title order={4} fw={600} c="white">
                            {courseTitle}
                        </Title>

                        <Stack gap={0}>
                            <Title order={5} fw={400} c="white">
                                Course Summary
                            </Title>
                            <Text c="dimmed">{courseDescription}</Text>
                        </Stack>

                        {keyOutcomes.length > 0 && (
                            <Stack gap="xs">
                                <Title order={5} fw={400} c="white">
                                    Key Outcomes
                                </Title>
                                <List>
                                    {keyOutcomes.map((outcome) => (
                                        <List.Item
                                            ml="sm"
                                            c="dimmed"
                                            key={outcome}
                                        >
                                            {outcome}
                                        </List.Item>
                                    ))}
                                </List>
                            </Stack>
                        )}

                        {topics.length > 0 && (
                            <Stack gap="xs">
                                <Title order={5} fw={400} c="white">
                                    Topics
                                </Title>
                                <List>
                                    {topics.map((topic) => (
                                        <List.Item
                                            ml="sm"
                                            c="dimmed"
                                            key={topic}
                                        >
                                            {topic}
                                        </List.Item>
                                    ))}
                                </List>
                            </Stack>
                        )}
                    </Stack>
                )}
            </Box>

            <Divider />

            <Group>
                <Button disabled>Complete Course</Button>
            </Group>

            <Space h="xl" />
        </Stack>
    );
};
