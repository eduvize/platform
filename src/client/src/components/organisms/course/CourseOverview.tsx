import { useMemo, useState } from "react";
import { useCourse } from "@context/course/hooks";
import {
    Button,
    Card,
    Container,
    Divider,
    Grid,
    Group,
    Radio,
    RingProgress,
    Space,
    Stack,
    Text,
    Title,
} from "@mantine/core";
import { useNavigate } from "react-router-dom";
import { CourseHero, ModuleListItem } from "@molecules";

export const CourseOverview = () => {
    const navigate = useNavigate();
    const {
        course: { id, modules, description, current_lesson_id },
    } = useCourse();

    const currentLesson = useMemo(() => {
        if (!current_lesson_id) return null;

        for (const module of modules) {
            for (const lesson of module.lessons) {
                if (lesson.id === current_lesson_id) {
                    return lesson;
                }
            }
        }

        return null;
    }, [current_lesson_id]);

    const currentModule = useMemo(() => {
        if (!currentLesson) return null;

        for (const module of modules) {
            for (const lesson of module.lessons) {
                if (lesson.id === currentLesson.id) {
                    return module;
                }
            }
        }

        return null;
    }, [currentLesson]);

    const getStatus = (moduleOrder: number) => {
        if (moduleOrder < currentModule!.order) {
            return "completed";
        }

        if (moduleOrder === currentModule!.order) {
            return "in-progress";
        }

        return "not-started";
    };

    const completedLessonsPercentage = useMemo(() => {
        let totalLessons = 0;
        let completedLessons = 0;

        modules.forEach((module) => {
            totalLessons += module.lessons.length;
            if (module.order < currentModule!.order) {
                completedLessons += module.lessons.length;
            } else if (module.order === currentModule!.order) {
                completedLessons += currentLesson!.order;
            }
        });

        return Math.round((completedLessons / totalLessons) * 100);
    }, [modules, currentModule, currentLesson]);

    const estimatedTimeRemaining = useMemo(() => {
        let totalMinutes = 0;
        let isCurrentLessonFound = false;

        for (const module of modules) {
            for (const lesson of module.lessons) {
                if (lesson.id === currentLesson?.id) {
                    isCurrentLessonFound = true;
                }
                if (isCurrentLessonFound) {
                    for (const section of lesson.sections) {
                        // Estimate time based on content length
                        // Assume 1 minute per 100 words
                        totalMinutes += Math.ceil(
                            section.content.split(" ").length / 100
                        );
                    }
                }
            }
        }

        if (totalMinutes < 60) {
            return { value: totalMinutes, unit: "min" };
        } else {
            return { value: Math.ceil(totalMinutes / 60), unit: "hr" };
        }
    }, [modules, currentLesson]);

    return (
        <Container size="sm" pt="xl">
            <Stack>
                <Stack gap="md">
                    <CourseHero />

                    <Card withBorder p="lg" px="xl">
                        <Space h="lg" />

                        <Stack>
                            <Title order={4} fw={500} c="white">
                                Course Summary
                            </Title>

                            <Text size="md" c="#c9c9c9">
                                {description}
                            </Text>

                            <Divider />

                            <Title order={4} fw={500} c="white">
                                Current lesson:
                            </Title>

                            <Grid>
                                <Grid.Col span={1}>
                                    <Stack
                                        h="100%"
                                        justify="center"
                                        align="center"
                                    >
                                        <Radio
                                            checked
                                            size="xl"
                                            variant="outline"
                                            styles={{
                                                radio: {
                                                    border: "2px solid #51cf66",
                                                    background: "transparent",
                                                },
                                                icon: {
                                                    color: "#51cf66",
                                                },
                                            }}
                                        />
                                    </Stack>
                                </Grid.Col>

                                <Grid.Col span={11}>
                                    <Stack gap={0}>
                                        <Title order={6} fw={500} c="white">
                                            {currentLesson?.title}
                                        </Title>

                                        <Text size="sm" c="dimmed">
                                            {currentLesson?.description}
                                        </Text>
                                    </Stack>
                                </Grid.Col>
                            </Grid>

                            <Group>
                                <Button
                                    variant="filled"
                                    bg="blue"
                                    fw={300}
                                    mt="xs"
                                    h={44}
                                    onClick={() => {
                                        navigate(
                                            `/dashboard/course/${id}/lesson/${currentLesson?.id}`
                                        );
                                    }}
                                >
                                    Continue Lesson
                                </Button>
                            </Group>
                        </Stack>
                    </Card>

                    <Card withBorder p="lg" px="xl">
                        <Stack>
                            <Group justify="center" gap="xl">
                                <Stack gap={0} align="center">
                                    <RingProgress
                                        size={180}
                                        thickness={7}
                                        sections={[
                                            {
                                                value: completedLessonsPercentage,
                                                color: "#51cf66",
                                            },
                                            {
                                                value:
                                                    100 -
                                                    completedLessonsPercentage,
                                                color: "transparent",
                                            },
                                        ]}
                                        label={
                                            <Text
                                                ff="Roboto"
                                                c="#51cf66"
                                                fw={900}
                                                ta="center"
                                                size="60px"
                                            >
                                                {completedLessonsPercentage}
                                            </Text>
                                        }
                                    />

                                    <Text
                                        ta="center"
                                        size="sm"
                                        c="#c9c9c9"
                                        w="50%"
                                    >
                                        % of lessons complete
                                    </Text>
                                </Stack>

                                <Stack gap={0} align="center">
                                    <RingProgress
                                        size={180}
                                        thickness={5}
                                        sections={[
                                            { value: 100, color: "#383838" },
                                        ]}
                                        label={
                                            <Group gap={0} justify="center">
                                                <Text
                                                    ff="Roboto"
                                                    c="#1479b2"
                                                    fw={900}
                                                    size="60px"
                                                >
                                                    {
                                                        estimatedTimeRemaining.value
                                                    }
                                                </Text>

                                                <Stack
                                                    h="100%"
                                                    justify="flex-end"
                                                >
                                                    <Text
                                                        size="24px"
                                                        fw={900}
                                                        c="#1479b2"
                                                        mt={26}
                                                    >
                                                        {
                                                            estimatedTimeRemaining.unit
                                                        }
                                                    </Text>
                                                </Stack>
                                            </Group>
                                        }
                                    />

                                    <Text
                                        ta="center"
                                        size="sm"
                                        c="#c9c9c9"
                                        w="60%"
                                    >
                                        estimated time remaining
                                    </Text>
                                </Stack>
                            </Group>

                            <Divider />

                            <Group justify="space-between">
                                <Text size="sm">
                                    course started: 10/05/2024
                                </Text>

                                <Text size="sm">
                                    course completed: --/--/----
                                </Text>
                            </Group>
                        </Stack>
                    </Card>
                </Stack>

                <Stack>
                    {modules.map((module, index) => (
                        <ModuleListItem
                            currentLesson={currentLesson!}
                            status={getStatus(module.order)}
                            onLessonSelect={(lessonId) => {
                                navigate(
                                    `/dashboard/course/${id}/lesson/${lessonId}`
                                );
                            }}
                            {...module}
                        />
                    ))}
                </Stack>
            </Stack>
        </Container>
    );
};
