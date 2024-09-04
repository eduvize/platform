import { ChatProvider, useChat } from "@context/chat";
import { useCourse, useLesson } from "@context/course/hooks";
import {
    Button,
    Card,
    Center,
    Container,
    Grid,
    Group,
    Space,
    Stack,
    Stepper,
    Text,
} from "@mantine/core";
import { ReadingMaterial } from "@molecules";
import { Chat } from "@organisms";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

interface LessonProps {
    courseId: string;
    lessonId: string;
}

export const Component = ({ courseId, lessonId }: LessonProps) => {
    const navigate = useNavigate();
    const { purge: purgeChatSession } = useChat();
    const {
        markSectionCompleted,
        course: { lesson_index },
    } = useCourse();
    const [isChatUsed, setIsChatUsed] = useState(false);
    const { title, description, sections, order } = useLesson(lessonId);
    const [section, setSection] = useState(lessonId ? lesson_index : 0);

    useEffect(() => {
        // TODO: Figure out what's wrong with useWindowScroll. Hack in the meantime!
        document
            .getElementById("root")!
            .scrollTo({ top: 0, behavior: "smooth" });

        purgeChatSession();
        setIsChatUsed(false);
    }, [section]);

    const handleNextSection = () => {
        setSection(section + 1);
    };

    return (
        <Container size={sections.length === 1 ? "lg" : "xl"}>
            <Grid mt="xl">
                {sections.length > 1 && (
                    <Grid.Col span={3} pr="xl" pt="xl">
                        <Stepper
                            mt="xl"
                            pt="md"
                            orientation="vertical"
                            active={section}
                        >
                            {sections.map((section, index) => (
                                <Stepper.Step
                                    key={index}
                                    label={section.title}
                                    description={section.description}
                                    styles={{
                                        stepLabel: {
                                            fontSize: 12,
                                        },
                                    }}
                                />
                            ))}
                        </Stepper>
                    </Grid.Col>
                )}

                <Grid.Col span={sections.length === 1 ? 12 : 9}>
                    <Stack>
                        <Group justify="space-between">
                            <Stack gap={0}>
                                <Text size="xl" fw={700}>
                                    Lesson {order + 1}: {title}
                                </Text>

                                <Text size="sm" c="dimmed">
                                    {description}
                                </Text>
                            </Stack>

                            <Button
                                variant="filled"
                                bg="dark"
                                onClick={() => {
                                    navigate(`/dashboard/course/${courseId}`);
                                }}
                            >
                                Back to modules
                            </Button>
                        </Group>

                        <Card
                            withBorder
                            p="xl"
                            mt={sections.length === 1 ? "xl" : undefined}
                        >
                            <ReadingMaterial>
                                {sections[section].content}
                            </ReadingMaterial>
                        </Card>

                        <Space h="xs" />

                        <Card withBorder>
                            <Chat
                                height={isChatUsed ? "500px" : "120px"}
                                greetingMessage="Have any questions about this section, or want to expand on any detail? Ask away!"
                                onMessageData={() => setIsChatUsed(true)}
                            />
                        </Card>

                        <Space h="sm" />

                        <Center>
                            {section > 0 && (
                                <Button
                                    variant="filled"
                                    bg="dark"
                                    c="dimmed"
                                    onClick={() => setSection(section - 1)}
                                    mr="xl"
                                >
                                    Previous Section
                                </Button>
                            )}

                            <Button
                                variant="gradient"
                                onClick={() => {
                                    markSectionCompleted(lessonId, section);

                                    if (section === sections.length - 1) {
                                        navigate(
                                            `/dashboard/course/${courseId}`
                                        );
                                        return;
                                    } else {
                                        handleNextSection();
                                    }
                                }}
                            >
                                {section === sections.length - 1
                                    ? "Complete Lesson"
                                    : "Next Section"}
                            </Button>
                        </Center>

                        <Space h="xl" />
                    </Stack>
                </Grid.Col>
            </Grid>
        </Container>
    );
};

export const Lesson = ({ courseId, lessonId }: LessonProps) => {
    return (
        <ChatProvider prompt="lesson" resourceId={lessonId}>
            <Component courseId={courseId} lessonId={lessonId} />
        </ChatProvider>
    );
};
