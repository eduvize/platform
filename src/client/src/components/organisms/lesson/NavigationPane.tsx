import { useCourse } from "@context/course/hooks";
import { Group, UnstyledButton, Divider, Box, Text } from "@mantine/core";
import { LessonNavItem } from "@molecules";
import { IconSquareMinusFilled } from "@tabler/icons-react";
import { useMemo } from "react";
import { Link } from "react-router-dom";

interface NavigationPaneProps {
    currentLessonId: string;
    currentSection: number;
    exerciseVisible?: boolean;
    onHide: () => void;
    onExerciseClick: () => void;
    onChangeSection: (section: number) => void;
}

export const NavigationPane = ({
    currentLessonId,
    currentSection,
    exerciseVisible,
    onHide,
    onExerciseClick,
    onChangeSection,
}: NavigationPaneProps) => {
    const { course } = useCourse();
    const { current_lesson_id } = course;

    const currentLesson = useMemo(() => {
        return course.modules
            .map((module) => module.lessons)
            .flat()
            .find((lesson) => lesson.id === current_lesson_id);
    }, [current_lesson_id]);

    const sections = currentLesson?.sections || [];

    const currentModule = useMemo(() => {
        return course.modules.find((module) =>
            module.lessons.some((lesson) => lesson.id === current_lesson_id)
        );
    }, [current_lesson_id]);

    return (
        <>
            <Group justify="space-between">
                <Text tt="uppercase" size="10px">
                    Navigation
                </Text>

                <UnstyledButton p={0} variant="transparent" onClick={onHide}>
                    <IconSquareMinusFilled color="#1479B2" />
                </UnstyledButton>
            </Group>

            <Divider />

            <Link
                to={`/dashboard/course/${course.id}`}
                style={{
                    color: "var(--mantine-color-blue-3)",
                    fontSize: "12px",
                }}
            >
                Back To Syllabus
            </Link>

            <Text size="xl" mt="lg" mb="md" c="white" fw="200">
                Module {currentModule!.order + 1}: {currentModule?.title}
            </Text>

            {currentModule?.lessons.map((lesson) => (
                <Box mb="xs">
                    <LessonNavItem
                        key={lesson.id}
                        {...lesson}
                        active={lesson.id === currentLessonId}
                        onSectionChange={(section) => {
                            if (section > sections.length - 1) {
                                onExerciseClick();
                            } else {
                                onChangeSection(section);
                            }
                        }}
                        activeSection={
                            currentSection + (exerciseVisible ? 1 : 0)
                        }
                    />
                </Box>
            ))}
        </>
    );
};
