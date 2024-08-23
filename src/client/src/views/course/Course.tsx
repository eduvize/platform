import { useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import {
    Accordion,
    Box,
    Card,
    Container,
    Group,
    List,
    ScrollArea,
    Stack,
    Title,
    Text,
    Button,
    ListItem,
    Tabs,
} from "@mantine/core";
import { CourseProvider } from "@context/course";
import { useCourse } from "@context/course/hooks";
import { ReadingMaterial } from "@molecules";

const Component = () => {
    const course = useCourse();
    const viewportRef = useRef<HTMLDivElement>(null);
    const [moduleIndex, setModuleIndex] = useState(0);
    const [lessonIndex, setLessonIndex] = useState(0);
    const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
    const [openedModuleIndex, setOpenedModule] = useState<number>(0);

    const currentModule = course?.modules[moduleIndex];
    const openedModule = course?.modules[openedModuleIndex];
    const currentLesson = currentModule?.lessons[lessonIndex];

    useEffect(() => {
        setTimeout(() => {
            viewportRef.current?.scrollTo({
                top: 0,
            });
        }, 300);
    }, [currentSectionIndex]);

    useEffect(() => {
        setCurrentSectionIndex(0);
    }, [moduleIndex, lessonIndex]);

    useEffect(() => {
        setOpenedModule(moduleIndex);
    }, [moduleIndex]);

    return (
        <Container size="xl" px="lg" mt="xl">
            <Stack>
                <Group>
                    <Box w="300px"></Box>

                    <Stack gap={0}>
                        <Title order={2}>{currentLesson?.title}</Title>
                        <Text c="dimmed" size="sm">
                            {currentLesson?.description}
                        </Text>
                    </Stack>
                </Group>

                <Group align="flex-start" wrap="nowrap">
                    <Box w="280px" mr="lg">
                        <Accordion
                            value={`module-${openedModuleIndex}`}
                            onChange={(name) =>
                                setOpenedModule(
                                    parseInt(name?.split("-")[1] || "0")
                                )
                            }
                        >
                            {course?.modules.map((module, mIndex) => (
                                <Accordion.Item value={`module-${mIndex}`}>
                                    <Accordion.Control>
                                        <Text size="sm">{module.title}</Text>
                                    </Accordion.Control>

                                    <Accordion.Panel>
                                        <List listStyleType="none">
                                            {openedModule?.lessons.map(
                                                (lesson, lIndex) => (
                                                    <ListItem>
                                                        <Button
                                                            variant="transparent"
                                                            size="compact-sm"
                                                            c={
                                                                mIndex ===
                                                                    moduleIndex &&
                                                                lIndex ===
                                                                    lessonIndex
                                                                    ? "blue"
                                                                    : "white"
                                                            }
                                                            onClick={() => {
                                                                setModuleIndex(
                                                                    mIndex
                                                                );
                                                                setLessonIndex(
                                                                    lIndex
                                                                );
                                                            }}
                                                        >
                                                            {lesson.title}
                                                        </Button>
                                                    </ListItem>
                                                )
                                            )}
                                        </List>
                                    </Accordion.Panel>
                                </Accordion.Item>
                            ))}
                        </Accordion>
                    </Box>

                    <Tabs
                        orientation="horizontal"
                        w="calc(100% - 420px)"
                        value={`section-${currentSectionIndex}`}
                        onChange={(value) =>
                            setCurrentSectionIndex(
                                parseInt(value?.split("-")[1] || "0")
                            )
                        }
                    >
                        <Tabs.List bg="dark" style={{ borderRadius: "6px" }}>
                            {currentModule?.lessons?.[
                                lessonIndex
                            ]?.sections?.map((section, index) => (
                                <Tabs.Tab
                                    title={section.title}
                                    value={`section-${index}`}
                                >
                                    <Text c="white" size="sm">
                                        {section.title}
                                    </Text>
                                </Tabs.Tab>
                            ))}
                        </Tabs.List>
                        <Box h="calc(100vh - 220px)">
                            <ScrollArea.Autosize
                                h="calc(100vh - 220px)"
                                viewportRef={viewportRef}
                                styles={{
                                    scrollbar: {
                                        width: "5px",
                                    },
                                }}
                            >
                                {currentModule?.lessons?.[
                                    lessonIndex
                                ]?.sections?.map((section, index) => (
                                    <Tabs.Panel value={`section-${index}`}>
                                        <Card shadow="xs" p="lg">
                                            <ReadingMaterial>
                                                {section.content}
                                            </ReadingMaterial>
                                        </Card>
                                    </Tabs.Panel>
                                ))}
                            </ScrollArea.Autosize>
                        </Box>
                    </Tabs>
                </Group>
            </Stack>
        </Container>
    );
};

export const Course = () => {
    const params = useParams();

    return (
        <CourseProvider courseId={params.course_id as string}>
            <Component />
        </CourseProvider>
    );
};
