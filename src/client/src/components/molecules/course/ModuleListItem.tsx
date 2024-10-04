import {
    Button,
    Card,
    Collapse,
    Grid,
    Group,
    List,
    ListItem,
    Stack,
    Tooltip,
    Text,
    Space,
} from "@mantine/core";
import { LessonDto, ModuleDto } from "@models/dto";
import {
    IconCircleCheckFilled,
    IconProgressCheck,
    IconLock,
} from "@tabler/icons-react";

interface ModuleListItemProps extends ModuleDto {
    currentLesson: LessonDto;
    status: "completed" | "in-progress" | "not-started";
    expanded: boolean;
    onToggle: () => void;
    onLessonSelect: (lessonId: string) => void;
    onExerciseSelect: (exerciseId: string) => void;
}

export const ModuleListItem = ({
    order,
    title,
    description,
    lessons,
    currentLesson,
    status,
    expanded,
    onToggle,
    onLessonSelect,
    onExerciseSelect,
}: ModuleListItemProps) => {
    const isLessonDisabled = (lessonOrder: number): boolean => {
        if (order === 0 && lessonOrder === 0) return false;

        if (status === "not-started") return true;

        if (lessonOrder > currentLesson.order) return true;

        return false;
    };

    const isLessonCompleted = (lessonOrder: number): boolean => {
        if (lessonOrder < currentLesson!.order) {
            return true;
        }

        return false;
    };

    return (
        <Card withBorder>
            <Grid>
                <Grid.Col span={12}>
                    <Stack gap={0}>
                        <Grid>
                            <Grid.Col
                                span="auto"
                                onClick={onToggle}
                                style={{ cursor: "pointer" }}
                            >
                                <Group justify="space-between">
                                    <Text size="lg">{title}</Text>

                                    {status === "completed" && (
                                        <IconCircleCheckFilled
                                            color="lightgreen"
                                            size={28}
                                        />
                                    )}
                                    {status === "in-progress" && (
                                        <IconProgressCheck
                                            color="goldenrod"
                                            size={28}
                                        />
                                    )}
                                    {status === "not-started" && (
                                        <Tooltip label="Unlock by completing previous modules">
                                            <IconLock color="gray" size={28} />
                                        </Tooltip>
                                    )}
                                </Group>
                            </Grid.Col>
                        </Grid>

                        <Text size="sm" c="dimmed">
                            {description}
                        </Text>
                    </Stack>
                </Grid.Col>

                <Collapse
                    in={expanded}
                    transitionDuration={300}
                    transitionTimingFunction="linear"
                >
                    <Grid.Col span={12}>
                        <List listStyleType="none">
                            {lessons.map((lesson, lessonIndex) => (
                                <Stack gap={0}>
                                    <ListItem key={lessonIndex}>
                                        <Button
                                            c={
                                                isLessonCompleted(lesson.order)
                                                    ? "lightgreen"
                                                    : isLessonDisabled(
                                                          lessonIndex
                                                      )
                                                    ? "dimmed"
                                                    : "blue"
                                            }
                                            variant="subtle"
                                            disabled={isLessonDisabled(
                                                lesson.order
                                            )}
                                            onClick={() =>
                                                onLessonSelect(lesson.id)
                                            }
                                        >
                                            {`Lesson ${lesson.order + 1}: ${
                                                lesson.title
                                            }`}
                                        </Button>
                                    </ListItem>
                                </Stack>
                            ))}
                        </List>
                    </Grid.Col>
                </Collapse>
            </Grid>
        </Card>
    );
};
