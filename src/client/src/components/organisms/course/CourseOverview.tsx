import { useMemo, useState } from "react";
import { useCourse } from "@context/course/hooks";
import { Card, Container, Stack, Text } from "@mantine/core";
import { useNavigate } from "react-router-dom";
import { CourseHero, ModuleListItem } from "@molecules";

export const CourseOverview = () => {
    const navigate = useNavigate();
    const {
        course: { id, modules, description, current_lesson_id, lesson_index },
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
    }, [current_lesson_id, lesson_index]);

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
    }, [currentLesson, lesson_index]);

    const getStatus = (moduleOrder: number) => {
        if (moduleOrder < currentModule!.order) {
            return "completed";
        }

        if (moduleOrder === currentModule!.order) {
            return "in-progress";
        }

        return "not-started";
    };

    // State to manage which modules are expanded
    const [expandedModules, setExpandedModules] = useState<{
        [key: number]: boolean;
    }>(
        modules.reduce((acc, module, index) => {
            return {
                ...acc,
                [index]: ["in-progress"].includes(getStatus(module.order)),
            };
        }, {})
    );

    const toggleModule = (index: number) => {
        setExpandedModules((prevState) => ({
            ...prevState,
            [index]: !prevState[index], // Toggle the specific module
        }));
    };

    return (
        <Container size="md" pt="xl">
            <Stack>
                <Stack gap="md">
                    <CourseHero />

                    <Card>
                        <Text size="md" c="white">
                            {description}
                        </Text>
                    </Card>
                </Stack>

                <Text tt="uppercase" size="xl">
                    Course Syllabus
                </Text>

                <Stack>
                    {modules.map((module, index) => (
                        <ModuleListItem
                            currentLesson={currentLesson!}
                            status={getStatus(module.order)}
                            expanded={expandedModules[index]}
                            onToggle={() => {
                                toggleModule(index);
                            }}
                            onLessonSelect={(lessonId) => {
                                navigate(
                                    `/dashboard/course/${id}/lesson/${lessonId}`
                                );
                            }}
                            onExerciseSelect={(exerciseId) => {
                                navigate(
                                    `/dashboard/course/${id}/exercise/${exerciseId}`
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
