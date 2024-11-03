import {
    Stack,
    Group,
    Button,
    Card,
    Box,
    Space,
    Text,
    Divider,
} from "@mantine/core";
import { ReadingMaterial } from "@atoms";
import { Playground } from "../../organisms/playground";
import { useExercise, useExerciseObjectives } from "@context/exercise/hooks";
import { CourseDto, LessonDto } from "@models/dto";
import { useEffect, useMemo } from "react";
import { useChat } from "@context/chat";

interface LessonContentProps {
    course: CourseDto;
    lesson: LessonDto;
    view: "lesson" | "exercise";
    currentSection: number;
    onComplete: () => void;
}

export const LessonContent = ({
    course,
    lesson,
    currentSection,
    view,
    onComplete,
}: LessonContentProps) => {
    const { sections } = lesson;
    const section = sections[currentSection];
    const exercise = useExercise();
    const objectives = useExerciseObjectives();
    const { setLessonId, setData } = useChat("lesson");

    useEffect(() => {
        setLessonId(lesson.id);
        setData({
            section: currentSection,
        });
    }, [lesson, currentSection]);

    const isLastLesson = useMemo(() => {
        return currentSection === sections.length - 1;
    }, [currentSection, sections]);

    const isLastLessonInCourse = useMemo(() => {
        if (!isLastLesson) return false;

        const lastModule = course?.modules.at(-1);

        return lastModule?.lessons.at(-1)?.id === lesson.id;
    }, [isLastLesson, course, lesson]);

    return (
        <Stack>
            <Group justify="space-between" wrap="nowrap">
                {view === "lesson" && (
                    <Stack gap={0}>
                        <Text size="xl" c="white">
                            {section.title}
                        </Text>

                        <Text size="sm">{section.description}</Text>
                    </Stack>
                )}

                {view === "exercise" && exercise && (
                    <Stack gap={0}>
                        <Text size="xl" fw={700}>
                            Exercise: {exercise.title}
                        </Text>

                        <Text size="sm">{exercise.summary}</Text>
                    </Stack>
                )}

                {currentSection === sections.length - 1 &&
                    (!exercise || objectives.every((x) => x.is_completed)) && (
                        <Button
                            fw="200"
                            size="sm"
                            style={{
                                fontSize: "12px",
                            }}
                            onClick={onComplete}
                        >
                            {isLastLessonInCourse
                                ? "Complete Course"
                                : "Complete Lesson"}
                        </Button>
                    )}
            </Group>

            <Card withBorder mt="md" p={0}>
                <Box
                    opacity={view === "exercise" ? 1 : 0}
                    pos={view === "exercise" ? "relative" : "fixed"}
                    right={view === "exercise" ? undefined : "100%"}
                >
                    <Playground height={800} />
                </Box>

                {view === "lesson" && (
                    <Box px="xl">
                        {typeof sections[currentSection]?.content ===
                        "string" ? (
                            <ReadingMaterial>
                                {sections[currentSection]?.content}
                            </ReadingMaterial>
                        ) : (
                            sections[currentSection]?.content
                        )}

                        <Divider mb="md" mt="md" />

                        <Group mb="lg">
                            {!isLastLesson && (
                                <Button onClick={onComplete}>Continue</Button>
                            )}
                            {isLastLesson && !isLastLessonInCourse && (
                                <Button onClick={onComplete}>
                                    Next Lesson
                                </Button>
                            )}
                            {isLastLessonInCourse && (
                                <Button onClick={onComplete}>
                                    Complete Course
                                </Button>
                            )}
                        </Group>
                    </Box>
                )}
            </Card>

            <Space h="sm" />
        </Stack>
    );
};
