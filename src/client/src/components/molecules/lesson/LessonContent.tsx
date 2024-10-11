import { Stack, Group, Button, Card, Box, Space, Text } from "@mantine/core";
import { ReadingMaterial } from "@atoms";
import { Playground } from "../../organisms/playground";
import { useExercise, useExerciseObjectives } from "@context/exercise/hooks";
import { LessonDto } from "@models/dto";

interface LessonContentProps {
    lesson: LessonDto;
    view: "lesson" | "exercise";
    currentSection: number;
    onComplete: () => void;
}

export const LessonContent = ({
    lesson,
    currentSection,
    view,
    onComplete,
}: LessonContentProps) => {
    const { sections } = lesson;
    const section = sections[currentSection];
    const exercise = useExercise();
    const objectives = useExerciseObjectives();

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
                                border: "1px solid #000",
                            }}
                            onClick={onComplete}
                        >
                            Complete Lesson
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
                    </Box>
                )}
            </Card>

            <Space h="sm" />
        </Stack>
    );
};
