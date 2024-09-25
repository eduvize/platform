import { ChatProvider, useChat } from "@context/chat";
import { useCourse, useLesson } from "@context/course/hooks";
import {
    Avatar,
    Box,
    Button,
    Card,
    Center,
    Checkbox,
    Container,
    Divider,
    Flex,
    Grid,
    Group,
    List,
    Space,
    Stack,
    Text,
    UnstyledButton,
} from "@mantine/core";
import { LessonItem, ReadingMaterial } from "@molecules";
import { Chat, NavigationPane, Playground } from "@organisms";
import { IconList, IconSquareMinusFilled } from "@tabler/icons-react";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import avatar from "./avatar.png";
import { ExerciseProvider } from "@context/exercise";
import { useExercise, useExerciseObjectives } from "@context/exercise/hooks";
import { useResizeObserver, useViewportSize } from "@mantine/hooks";
import { CourseProvider } from "@context/course";

interface LessonProps {
    courseId: string;
    lessonId: string;
}

type Panel = "module" | "instructor";

export const Component = ({ courseId, lessonId }: LessonProps) => {
    const navigate = useNavigate();
    const { purge: purgeChatSession } = useChat();
    const { markLessonComplete: markSectionCompleted, course } = useCourse();
    const exercise = useExercise();
    const objectives = useExerciseObjectives();
    const [isChatUsed, setIsChatUsed] = useState(false);
    const { title, description, sections, order, exercises } =
        useLesson(lessonId);
    const [section, setSection] = useState(0);
    const [showExercise, setShowExercise] = useState(false);
    const currentModule = course.modules.find((module) =>
        module.lessons.some((lesson) => lesson.id === lessonId)
    );
    const [panels, setPanels] = useState<Panel[]>(["instructor", "module"]);
    const [chatAreaRef, chatAreaRect] = useResizeObserver();
    const [instructorPaneRef, instructorPaneRect] = useResizeObserver();
    const { height: viewportHeight } = useViewportSize();
    const [chatHeight, setChatHeight] = useState<number>(500);

    useEffect(() => {
        // TODO: Figure out what's wrong with useWindowScroll. Hack in the meantime!
        document
            .getElementById("root")!
            .scrollTo({ top: 0, behavior: "smooth" });

        purgeChatSession();
        setIsChatUsed(false);
    }, [section, showExercise]);

    useEffect(() => {
        if (chatAreaRect) {
            setChatHeight(
                viewportHeight -
                    chatAreaRect.top -
                    instructorPaneRect.height -
                    200
            );
        }
    }, [chatAreaRect, viewportHeight, instructorPaneRect]);

    const handleCompleteSection = () => {
        markSectionCompleted(lessonId);

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

    return (
        <Container fluid>
            <Grid mt="lg" gutter="lg">
                <Grid.Col span={panels.includes("module") ? 3 : 0.5}>
                    {panels.includes("module") && (
                        <Box pos="absolute" w="23%">
                            <NavigationPane
                                currentLessonId={lessonId}
                                currentSection={section}
                                exerciseVisible={showExercise}
                                onHide={() => {
                                    setPanels(
                                        panels.filter((x) => x !== "module")
                                    );
                                }}
                                onExerciseClick={() => {
                                    setShowExercise(true);
                                    setSection(sections.length - 1);
                                }}
                                onChangeSection={(section) => {
                                    setSection(section);
                                    setShowExercise(false);
                                }}
                            />
                        </Box>
                    )}

                    {!panels.includes("module") && (
                        <Group justify="center" pos="fixed">
                            <UnstyledButton
                                mt="md"
                                variant="transparent"
                                p={0}
                                onClick={() => setPanels([...panels, "module"])}
                            >
                                <IconList color="white" size={32} />
                            </UnstyledButton>
                        </Group>
                    )}
                </Grid.Col>

                <Grid.Col
                    span={
                        6 +
                        (panels.includes("module") ? 0 : 2.5) +
                        (panels.includes("instructor") ? 0 : 2.5)
                    }
                >
                    <Stack>
                        <Group justify="space-between" wrap="nowrap">
                            {!showExercise && (
                                <Stack gap={0}>
                                    <Text size="xl" c="white">
                                        Lesson {order + 1}: {title}
                                    </Text>

                                    <Text size="sm">{description}</Text>
                                </Stack>
                            )}

                            {showExercise && exercise && (
                                <Stack gap={0}>
                                    <Text size="xl" fw={700}>
                                        Exercise: {exercise.title}
                                    </Text>

                                    <Text size="sm">{exercise.summary}</Text>
                                </Stack>
                            )}

                            {section === sections.length - 1 &&
                                (!exercise ||
                                    objectives.every(
                                        (x) => x.is_completed
                                    )) && (
                                    <Button
                                        fw="200"
                                        size="sm"
                                        style={{
                                            fontSize: "12px",
                                            border: "1px solid #000",
                                        }}
                                        onClick={handleCompleteSection}
                                    >
                                        Complete Lesson
                                    </Button>
                                )}
                        </Group>

                        <Card withBorder mt="md" p={0}>
                            <Box
                                opacity={showExercise ? 1 : 0}
                                pos={showExercise ? "relative" : "fixed"}
                                right={showExercise ? undefined : "100%"}
                            >
                                <Playground height="800px" />
                            </Box>

                            {!showExercise && (
                                <Box px="xl">
                                    <ReadingMaterial>
                                        {sections[section]?.content}
                                    </ReadingMaterial>
                                </Box>
                            )}
                        </Card>

                        <Space h="sm" />
                    </Stack>
                </Grid.Col>

                <Grid.Col span={panels.includes("instructor") ? 3 : 0.5}>
                    {panels.includes("instructor") && (
                        <Stack
                            justify="space-between"
                            pos="absolute"
                            h="calc(100% - 100px)"
                            w="23.5%"
                        >
                            <Flex direction="column" flex="1 0 auto">
                                <Flex
                                    direction="column"
                                    ref={instructorPaneRef}
                                >
                                    <Group justify="space-between">
                                        <Text tt="uppercase" size="10px">
                                            Instructor
                                        </Text>

                                        <Button
                                            p={0}
                                            variant="transparent"
                                            onClick={() =>
                                                setPanels(
                                                    panels.filter(
                                                        (x) =>
                                                            x !== "instructor"
                                                    )
                                                )
                                            }
                                        >
                                            <IconSquareMinusFilled color="#1479B2" />
                                        </Button>
                                    </Group>
                                    <Divider mb="xl" />

                                    {exercise && showExercise && (
                                        <Card withBorder mb="xl">
                                            <Text size="lg">
                                                Exercise Task List
                                            </Text>
                                            <Text size="xs" c="dimmed">
                                                Complete the following
                                                objectives to finish this
                                                exercise. If you need assistant,
                                                ask your instructor.
                                            </Text>

                                            <>
                                                <Space h="xl" />

                                                <List listStyleType="none">
                                                    {objectives.map(
                                                        ({
                                                            objective,
                                                            is_completed,
                                                        }) => (
                                                            <Checkbox
                                                                label={
                                                                    objective
                                                                }
                                                                checked={
                                                                    is_completed
                                                                }
                                                                mb="sm"
                                                            />
                                                        )
                                                    )}
                                                </List>
                                            </>
                                        </Card>
                                    )}
                                </Flex>

                                <Flex pos="relative" flex="1 1 auto" mt="xl">
                                    <Avatar
                                        pos="absolute"
                                        top="-55px"
                                        left="50%"
                                        ml="-42px"
                                        src={avatar}
                                        size="xl"
                                        radius="99999"
                                        bg="black"
                                        p="sm"
                                        styles={{
                                            root: {
                                                zIndex: 9999,
                                            },
                                        }}
                                    />
                                    <Card
                                        withBorder
                                        ref={chatAreaRef}
                                        pos="relative"
                                        w="100%"
                                        pt="xl"
                                    >
                                        <Chat
                                            maxHeight={chatHeight}
                                            greetingMessage="Let me know if you have any questions!"
                                            onMessageData={() =>
                                                setIsChatUsed(true)
                                            }
                                        />
                                    </Card>
                                </Flex>
                            </Flex>
                        </Stack>
                    )}

                    {!panels.includes("instructor") && (
                        <Group justify="center" pos="fixed">
                            <UnstyledButton
                                variant="transparent"
                                p={0}
                                onClick={() =>
                                    setPanels([...panels, "instructor"])
                                }
                            >
                                <Avatar
                                    src={avatar}
                                    size="lg"
                                    radius="99999"
                                    p="xs"
                                    bg="black"
                                />
                            </UnstyledButton>
                        </Group>
                    )}
                </Grid.Col>
            </Grid>
        </Container>
    );
};

export const Lesson = () => {
    const params = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        if (!params.course_id || !params.lesson_id) {
            navigate("/dashboard/courses");
        }
    }, []);

    if (!params.course_id || !params.lesson_id) {
        return null;
    }

    return (
        <CourseProvider courseId={params.course_id}>
            <ExerciseProvider lessonId={params.lesson_id}>
                <ChatProvider prompt="lesson" resourceId={params.lesson_id}>
                    <Component
                        courseId={params.course_id}
                        lessonId={params.lesson_id}
                    />
                </ChatProvider>
            </ExerciseProvider>
        </CourseProvider>
    );
};
