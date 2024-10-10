import { ChatProvider, useChat } from "@context/chat";
import { useCourse, useLesson } from "@context/course/hooks";
import {
    Avatar,
    Box,
    Container,
    Grid,
    Group,
    UnstyledButton,
} from "@mantine/core";
import { InstructorPane, LessonContent, NavigationPane } from "@organisms";
import { IconList } from "@tabler/icons-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ExerciseProvider } from "@context/exercise";
import { CourseProvider } from "@context/course";
const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;

interface LessonProps {
    courseId: string;
    lessonId: string;
}

type Panel = "module" | "instructor";

export const Component = (props: LessonProps) => {
    const { courseId, lessonId } = props;
    const navigate = useNavigate();
    const { instructorId } = useChat();
    const { markLessonComplete: markSectionCompleted } = useCourse();
    const { sections, exercises } = useLesson(lessonId);
    const [section, setSection] = useState(0);
    const [showExercise, setShowExercise] = useState(false);
    const [panels, setPanels] = useState<Panel[]>(["instructor", "module"]);

    useEffect(() => {
        // TODO: Figure out what's wrong with useWindowScroll. Hack in the meantime!
        document
            .getElementById("root")!
            .scrollTo({ top: 0, behavior: "smooth" });
    }, [section, showExercise]);

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
                    <LessonContent
                        lessonId={lessonId}
                        currentSection={section}
                        view={showExercise ? "exercise" : "lesson"}
                        onComplete={handleCompleteSection}
                    />
                </Grid.Col>

                <Grid.Col span={panels.includes("instructor") ? 3 : 0.5}>
                    {panels.includes("instructor") && (
                        <InstructorPane
                            onHide={() => {
                                setPanels(
                                    panels.filter((x) => x !== "instructor")
                                );
                            }}
                            view={showExercise ? "exercise" : "lesson"}
                        />
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
                                    src={`${apiEndpoint}/instructors/${instructorId}/profile-photo`}
                                    size="lg"
                                    radius="xl"
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
