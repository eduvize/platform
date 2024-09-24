import { ChatProvider, useChat } from "@context/chat";
import { useCourse, useLesson } from "@context/course/hooks";
import { PlaygroundProvider } from "@context/playground";
import {
    Box,
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
import { Chat, Exercise } from "@organisms";
import { IconHammer } from "@tabler/icons-react";
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
    const { title, description, sections, order, exercises } =
        useLesson(lessonId);
    const [section, setSection] = useState(lessonId ? lesson_index : 0);
    const [showExercise, setShowExercise] = useState(false);

    useEffect(() => {
        // TODO: Figure out what's wrong with useWindowScroll. Hack in the meantime!
        document
            .getElementById("root")!
            .scrollTo({ top: 0, behavior: "smooth" });

        purgeChatSession();
        setIsChatUsed(false);
    }, [section, showExercise]);

    const handleCompleteSection = () => {
        markSectionCompleted(lessonId, section);

        if (section === sections.length - 1) {
            if (exercises.length > 0) {
                if (!showExercise) {
                    setShowExercise(true);
                } else {
                    navigate(`/dashboard/course/${courseId}`);
                }
            } else {
                navigate(`/dashboard/course/${courseId}`);
            }
        } else {
            setSection(section + 1);
        }
    };

    const handlePrevious = () => {
        if (showExercise) {
            setShowExercise(false);
        } else if (section > 0) {
            setSection(section - 1);
        }
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
                            active={section + (showExercise ? 1 : 0)}
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

                            {exercises.length > 0 &&
                                exercises.map((exercise, index) => (
                                    <Stepper.Step
                                        key={index}
                                        label="Exercise"
                                        description={exercise.title}
                                        icon={<IconHammer />}
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
                            mt={sections.length === 1 ? "xl" : undefined}
                            p={0}
                        >
                            <Box
                                opacity={showExercise ? 1 : 0}
                                pos={showExercise ? "relative" : "fixed"}
                                right={showExercise ? undefined : "100%"}
                            >
                                <Exercise exerciseId={exercises[0].id} />
                            </Box>

                            {!showExercise && (
                                <Box p="xl">
                                    <ReadingMaterial>
                                        {sections[section].content}
                                    </ReadingMaterial>
                                </Box>
                            )}
                        </Card>

                        <Space h="xs" />

                        <Card withBorder>
                            <Chat
                                height={isChatUsed ? "500px" : "120px"}
                                greetingMessage="Let me know if you have any questions!"
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
                                    onClick={handlePrevious}
                                    mr="xl"
                                >
                                    Previous Section
                                </Button>
                            )}

                            <Button
                                variant="gradient"
                                onClick={handleCompleteSection}
                            >
                                {section === sections.length - 1
                                    ? exercises.length > 0
                                        ? showExercise
                                            ? "Complete Lesson"
                                            : "Continue to Exercise"
                                        : "Complete Lesson"
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
