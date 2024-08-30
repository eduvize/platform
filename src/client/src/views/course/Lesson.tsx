import { useCourse, useLesson } from "@context/course/hooks";
import {
    Button,
    Card,
    Center,
    Container,
    Grid,
    Group,
    Space,
    Stack,
    Stepper,
    Text,
} from "@mantine/core";
import { useWindowScroll } from "@mantine/hooks";
import { ReadingMaterial } from "@molecules";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getCumulativeLessonIndex } from "./getCumulativeLessonIndex";

interface LessonProps {
    courseId: string;
    lessonId: string;
}

export const Lesson = ({ courseId, lessonId }: LessonProps) => {
    const navigate = useNavigate();
    const course = useCourse();
    const [scroll, scrollTo] = useWindowScroll();
    const { title, description, sections } = useLesson(lessonId);
    const [section, setSection] = useState(0);
    const cumulativeIndex = getCumulativeLessonIndex(course, lessonId) + 1;

    useEffect(() => {
        // TODO: Figure out what's wrong with useWindowScroll. Hack in the meantime!
        document
            .getElementById("root")!
            .scrollTo({ top: 0, behavior: "smooth" });
    }, [section]);

    const handleNextSection = () => {
        setSection(section + 1);
    };

    return (
        <Container size={sections.length === 1 ? "lg" : "xl"}>
            <Grid mt="xl">
                {sections.length > 1 && (
                    <Grid.Col span={3} pr="xl" pt="xl">
                        <Stepper
                            mt="xl"
                            pt="md"
                            orientation="vertical"
                            active={section}
                            onStepClick={setSection}
                        >
                            {sections.map((section, index) => (
                                <Stepper.Step
                                    key={index}
                                    label={section.title}
                                    description={section.description}
                                    styles={{
                                        stepLabel: {
                                            fontSize: 12,
                                        },
                                    }}
                                />
                            ))}
                        </Stepper>
                    </Grid.Col>
                )}

                <Grid.Col span="auto">
                    <Stack>
                        <Group justify="space-between">
                            <Stack gap={0}>
                                <Text size="xl" fw={700}>
                                    Lesson {cumulativeIndex}: {title}
                                </Text>

                                <Text size="sm" c="dimmed">
                                    {description}
                                </Text>
                            </Stack>

                            <Button
                                variant="filled"
                                bg="dark"
                                onClick={() => {
                                    navigate(`/dashboard/course/${courseId}`);
                                }}
                            >
                                Back to modules
                            </Button>
                        </Group>

                        <Card
                            withBorder
                            p="xl"
                            mt={sections.length === 1 ? "xl" : undefined}
                        >
                            <ReadingMaterial>
                                {sections[section].content}
                            </ReadingMaterial>
                        </Card>

                        <Space h="sm" />

                        <Center>
                            {section === sections.length - 1 && (
                                <Button variant="gradient">
                                    Finish Lesson
                                </Button>
                            )}

                            {section < sections.length - 1 && (
                                <Button
                                    onClick={handleNextSection}
                                    variant="gradient"
                                >
                                    Continue
                                </Button>
                            )}
                        </Center>

                        <Space h="xl" />
                    </Stack>
                </Grid.Col>
            </Grid>
        </Container>
    );
};
