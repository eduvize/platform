import { useEffect, useMemo, useRef, useState } from "react";
import { Chat } from "@organisms";
import { ChatProvider, useLastToolResult } from "@context/chat";
import { ChatTool } from "@models/enums";
import {
    Accordion,
    Box,
    Card,
    Grid,
    List,
    ListItem,
    Text,
} from "@mantine/core";
import { Course } from "@models/dto";

const Component = () => {
    const containerRef = useRef<HTMLDivElement>(null);
    const outline = useLastToolResult<Course>(ChatTool.ProvideCourseOutline);

    return (
        <Grid>
            <Grid.Col span={8}>
                <Box px="md">
                    <Chat
                        height={`calc(100vh - 8em)`}
                        toolDescriptionMap={{
                            [ChatTool.ProvideCourseOutline]:
                                "Revising your course plan...",
                        }}
                    />
                </Box>
            </Grid.Col>

            <Grid.Col span={4}>
                {outline && (
                    <Card withBorder h="100%">
                        <Text size="xl">{outline.title}</Text>

                        <Text size="sm" c="dimmed">
                            {outline.description}
                        </Text>

                        <Accordion>
                            {outline.modules.map((module, index) => (
                                <Accordion.Item
                                    key={module.title}
                                    value={module.title}
                                >
                                    <Accordion.Control pl={0}>
                                        <Text size="sm">
                                            Module {index + 1}: {module.title}
                                        </Text>
                                    </Accordion.Control>

                                    <Accordion.Panel>
                                        <List listStyleType="none">
                                            {module.lessons.map(
                                                (lesson, index) => (
                                                    <ListItem
                                                        key={lesson.title}
                                                    >
                                                        <Text size="md">
                                                            {lesson.title}
                                                        </Text>
                                                        <Text
                                                            size="sm"
                                                            c="dimmed"
                                                        >
                                                            {lesson.description}
                                                        </Text>
                                                    </ListItem>
                                                )
                                            )}
                                        </List>
                                    </Accordion.Panel>
                                </Accordion.Item>
                            ))}
                        </Accordion>
                    </Card>
                )}
            </Grid.Col>
        </Grid>
    );
};

export const CoursePlanner = () => (
    <ChatProvider>
        <Component />
    </ChatProvider>
);
