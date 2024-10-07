import { Card, Grid, Stack, Text, Stepper, Box, Radio } from "@mantine/core";
import { LessonDto, ModuleDto } from "@models/dto";
import { IconCircleCheckFilled, IconLock } from "@tabler/icons-react";

interface ModuleListItemProps extends ModuleDto {
    currentLesson: LessonDto;
    status: "completed" | "in-progress" | "not-started";
    onLessonSelect: (lessonId: string) => void;
    onExerciseSelect: (exerciseId: string) => void;
}

export const ModuleListItem = ({
    currentLesson,
    title,
    description,
    lessons,
    status,
}: ModuleListItemProps) => {
    const isModuleCompleted = status === "completed";

    const activeIndex = isModuleCompleted
        ? lessons.length - 1
        : lessons.findIndex((lesson) => lesson.order === currentLesson.order);

    return (
        <Card withBorder>
            <Grid>
                <Grid.Col span={12}>
                    <Stack gap={0}>
                        <Grid>
                            <Grid.Col span="auto" style={{ cursor: "pointer" }}>
                                <Text size="lg" c="white">
                                    {title}
                                </Text>
                            </Grid.Col>
                        </Grid>

                        <Text size="sm" c="#c9c9c9">
                            {description}
                        </Text>
                    </Stack>
                </Grid.Col>

                <Grid.Col span={12}>
                    <Stepper
                        active={
                            isModuleCompleted ? lessons.length + 1 : activeIndex
                        }
                        color="green"
                        orientation="vertical"
                    >
                        {lessons.map((lesson, lessonIndex) => (
                            <Stepper.Step
                                label={`Lesson ${lesson.order + 1}: ${
                                    lesson.title
                                }`}
                                description={lesson.description}
                                completedIcon={
                                    <Box pos="relative" w={32} h={32} left={-1}>
                                        <Box
                                            pos="absolute"
                                            top={8}
                                            left={10}
                                            bg="white"
                                            w={16}
                                            h={16}
                                        ></Box>

                                        <IconCircleCheckFilled
                                            color="#51cf66"
                                            size={36}
                                            style={{
                                                position: "absolute",
                                            }}
                                        />
                                    </Box>
                                }
                                progressIcon={
                                    <Radio
                                        checked
                                        size="lg"
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
                                }
                                icon={
                                    <Box
                                        style={{
                                            border: "1px solid #3d3d3d",
                                            width: 32,
                                            height: 32,
                                            borderRadius: "50%",
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                        }}
                                    >
                                        <IconLock size={18} />
                                    </Box>
                                }
                                styles={{
                                    stepIcon: {
                                        padding: 0,
                                        backgroundColor: "transparent",
                                        borderColor: "transparent",
                                    },
                                    stepWrapper: {
                                        padding: 0,
                                    },
                                    stepLabel: {
                                        fontSize: "0.9rem",
                                        fontWeight: 500,
                                        color: "#fff",
                                    },
                                    stepDescription: {
                                        fontSize: "0.8rem",
                                        color: "#6d6d6d",
                                    },
                                }}
                            />
                        ))}
                    </Stepper>
                </Grid.Col>
            </Grid>
        </Card>
    );
};
