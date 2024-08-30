import { useState } from "react";
import { useCourse } from "@context/course/hooks";
import {
    Button,
    Card,
    Container,
    Grid,
    Group,
    List,
    ListItem,
    Stack,
    Text,
    Tooltip,
    Collapse,
} from "@mantine/core";
import { ModuleDto } from "@models/dto";
import {
    IconCircleCheckFilled,
    IconLock,
    IconProgressCheck,
} from "@tabler/icons-react";
import { useNavigate } from "react-router-dom";
import { CourseHero } from "@molecules";

export const CourseOverview = () => {
    const navigate = useNavigate();
    const { id, modules, description } = useCourse();

    let lessonCounter = 0;

    const noModulesStarted = modules.every((module) =>
        module.lessons.every((lesson) => !lesson.is_completed)
    );

    const getCompleted = (moduleIndex: number) =>
        modules[moduleIndex].lessons.every((lesson) => lesson.is_completed);

    const getIsInProgress = (moduleIndex: number) =>
        (modules[moduleIndex].lessons.some((lesson) => lesson.is_completed) &&
            !getCompleted(moduleIndex)) ||
        (moduleIndex === 0 && noModulesStarted);

    // State to manage which modules are expanded
    const [expandedModules, setExpandedModules] = useState<{
        [key: number]: boolean;
    }>(
        modules.reduce((acc, module, index) => {
            return {
                ...acc,
                [index]: getIsInProgress(index),
            };
        }, {})
    );

    const toggleModule = (index: number) => {
        setExpandedModules((prevState) => ({
            ...prevState,
            [index]: !prevState[index], // Toggle the specific module
        }));
    };

    const isLessonDisabled = (
        moduleIndex: number,
        lessonIndex: number
    ): boolean => {
        if (moduleIndex === 0 && lessonIndex === 0 && noModulesStarted) {
            return false;
        }

        if (lessonIndex > 0) {
            return !modules[moduleIndex].lessons[lessonIndex - 1].is_completed;
        }

        if (moduleIndex > 0) {
            return !getCompleted(moduleIndex - 1);
        }

        return false;
    };

    const ModuleItem = ({
        title,
        description,
        lessons,
        index,
    }: ModuleDto & { index: number }) => {
        const isComplete = getCompleted(index);
        const isInProgress =
            (getIsInProgress(index) ||
                (index === 0 &&
                    !modules.every(
                        (_, i) => getCompleted(i) || getIsInProgress(i)
                    ))) &&
            !isComplete;
        const isExpanded = expandedModules[index];

        return (
            <Card withBorder>
                <Grid>
                    <Grid.Col span={12}>
                        <Stack gap={0}>
                            <Grid>
                                <Grid.Col
                                    span="auto"
                                    onClick={() => toggleModule(index)}
                                    style={{ cursor: "pointer" }}
                                >
                                    <Group justify="space-between">
                                        <Text size="lg">{title}</Text>

                                        {isComplete && (
                                            <IconCircleCheckFilled
                                                color="lightgreen"
                                                size={28}
                                            />
                                        )}
                                        {isInProgress && (
                                            <IconProgressCheck
                                                color="goldenrod"
                                                size={28}
                                            />
                                        )}
                                        {!isComplete && !isInProgress && (
                                            <Tooltip label="Unlock by completing previous modules">
                                                <IconLock
                                                    color="gray"
                                                    size={28}
                                                />
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
                        in={isExpanded}
                        transitionDuration={300}
                        transitionTimingFunction="linear"
                    >
                        <Grid.Col span={12}>
                            <List listStyleType="none">
                                {lessons.map((lesson, lessonIndex, array) => (
                                    <ListItem key={lessonIndex}>
                                        <Button
                                            c={
                                                lesson.is_completed
                                                    ? "lightgreen"
                                                    : isLessonDisabled(
                                                          index,
                                                          lessonIndex
                                                      )
                                                    ? "dimmed"
                                                    : "blue"
                                            }
                                            variant="subtle"
                                            disabled={isLessonDisabled(
                                                index,
                                                lessonIndex
                                            )}
                                            onClick={() =>
                                                navigate(
                                                    `/dashboard/course/${id}/lesson/${lesson.id}`
                                                )
                                            }
                                        >
                                            {`Lesson ${++lessonCounter}: ${
                                                lesson.title
                                            }`}
                                        </Button>
                                    </ListItem>
                                ))}
                            </List>
                        </Grid.Col>
                    </Collapse>
                </Grid>
            </Card>
        );
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
                        <ModuleItem key={index} index={index} {...module} />
                    ))}
                </Stack>
            </Stack>
        </Container>
    );
};
