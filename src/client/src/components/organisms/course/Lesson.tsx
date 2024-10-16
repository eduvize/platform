import { useChat } from "@context/chat";
import { useCourse } from "@context/course/hooks";
import {
    Avatar,
    Box,
    Container,
    Grid,
    Group,
    UnstyledButton,
} from "@mantine/core";
import { InstructorPane, LessonContent, NavigationPane } from "@molecules";
import { IconList } from "@tabler/icons-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { CourseDto, LessonDto } from "@models/dto";
const apiEndpoint = import.meta.env.VITE_API_ENDPOINT;

type Panel = "module" | "instructor";

interface ComponentProps extends LessonDto {
    course: CourseDto;
    hideNumberedLabels?: boolean;
    hideInstructor?: boolean;
    section?: number;
    onSectionChange?: (section: number) => void;
}

export const Lesson = (props: ComponentProps) => {
    const navigate = useNavigate();
    const { instructorId } = useChat();
    const { markLessonComplete: markSectionCompleted } = useCourse();
    const [section, setSection] = useState(props.section ?? 0);
    const [showExercise, setShowExercise] = useState(false);
    const [panels, setPanels] = useState<Panel[]>(["instructor", "module"]);

    const {
        id: lessonId,
        sections,
        exercises,
        course,
        hideNumberedLabels,
        hideInstructor,
        onSectionChange,
    } = props;

    useEffect(() => {
        // TODO: Figure out what's wrong with useWindowScroll. Hack in the meantime!
        document
            .getElementById("root")!
            .scrollTo({ top: 0, behavior: "smooth" });
    }, [section, showExercise]);

    useEffect(() => {
        if (typeof props.section === "undefined") {
            return;
        }

        setSection(props.section);
    }, [props.section]);

    const handleCompleteSection = () => {
        markSectionCompleted(lessonId);

        if (section === sections.length - 1) {
            if (exercises.length > 0) {
                if (!showExercise) {
                    setShowExercise(true);
                } else {
                    navigate(`/dashboard/course/${course.id}`);
                }
            } else {
                navigate(`/dashboard/course/${course.id}`);
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
                                course={course}
                                currentLessonId={lessonId}
                                currentSection={section}
                                exerciseVisible={showExercise}
                                hideNumberedLabels={hideNumberedLabels}
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

                                    onSectionChange?.(section);
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
                        lesson={props}
                        currentSection={section}
                        view={showExercise ? "exercise" : "lesson"}
                        onComplete={handleCompleteSection}
                    />
                </Grid.Col>

                <Grid.Col
                    span={
                        panels.includes("instructor") && !!hideInstructor
                            ? 3
                            : 0.5
                    }
                >
                    {panels.includes("instructor") && !hideInstructor && (
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
