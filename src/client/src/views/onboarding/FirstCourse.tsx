import { useChat, useToolCallEffect } from "@context/chat";
import {
    Stack,
    Title,
    Text,
    Space,
    Divider,
    Group,
    Button,
    Box,
    List,
    Stepper,
} from "@mantine/core";
import { ChatTool } from "@models/enums";
import { IconConfetti } from "@tabler/icons-react";
import { useMemo, useState } from "react";
import { RingStatistic } from "../../components/atoms/course";
import { CheckboxStepper } from "@molecules";

export const FirstCourse = () => {
    const [courseTitle, setCourseTitle] = useState<string>("");
    const [courseDescription, setCourseDescription] = useState<string>("");
    const [keyOutcomes, setKeyOutcomes] = useState<string[]>([]);
    const [topics, setTopics] = useState<string[]>([]);
    const [isCourseCreated, setIsCourseCreated] = useState<boolean>(false);

    const shouldDisplayCourseInfo = useMemo(() => {
        return courseTitle.length > 0 && courseDescription.length > 0;
    }, [courseTitle, courseDescription]);

    useToolCallEffect(ChatTool.CourseBuilderSetCourseTitle, (result) => {
        setCourseTitle(result.title);
    });

    useToolCallEffect(ChatTool.CourseBuilderSetCourseDescription, (result) => {
        setCourseDescription(result.description);
    });

    useToolCallEffect(ChatTool.CourseBuilderSetCourseKeyOutcomes, (result) => {
        setKeyOutcomes(result.outcomes);
    });

    useToolCallEffect(ChatTool.CourseBuilderSetCourseTopics, (result) => {
        setTopics(result.topics);
    });

    useToolCallEffect(ChatTool.CourseBuilderCourseGenerated, () => {
        setIsCourseCreated(true);
    });

    const areAllStepsComplete = useMemo(() => {
        return (
            courseTitle.length > 0 &&
            courseDescription.length > 0 &&
            keyOutcomes.length > 0 &&
            topics.length > 0
        );
    }, [courseTitle, courseDescription, keyOutcomes, topics]);

    if (isCourseCreated) {
        return (
            <Stack pt="lg">
                <Group>
                    <IconConfetti color="#1479B2" />

                    <Title order={3} fw={400} c="white">
                        Congratulations!!
                    </Title>
                </Group>

                <Text>
                    Congratulations on completing <b>The First Course</b>
                </Text>

                <Group justify="center" gap="xl">
                    <RingStatistic value={100} label="% of lessons complete" />
                    <RingStatistic
                        hideProgress
                        value={2}
                        unit="hours"
                        label="longest session"
                        thickness={2}
                    />
                    <RingStatistic
                        hideProgress
                        value={15}
                        unit="min"
                        label="average session time"
                        borderColor="#424242"
                        textColor="#1479B2"
                        thickness={2}
                    />
                </Group>

                <Space h="xl" />

                <Title order={3} c="white" fw={400}>
                    Key Takeaways
                </Title>

                <CheckboxStepper active={2}>
                    <Stepper.Step
                        label="You're ready to start using Eduvize!"
                        description="This course has given you all the basics about Eduvize"
                    />
                    <Stepper.Step
                        label="You've started to get to know Kyle."
                        description="You and Kyle has a great conversation. You can keep working with Kyle on your next classes, or swap out your instructor at any time."
                    />
                </CheckboxStepper>

                <Title order={3} c="white" fw={400}>
                    Next Steps
                </Title>

                <CheckboxStepper active={1}>
                    <Stepper.Step
                        label="Start your course."
                        description={`You've worked with Kyle to create ${courseTitle}. You can start your course by clicking the button below.`}
                    />
                </CheckboxStepper>

                <Divider />

                <Group>
                    <Button>Check out my Courses</Button>
                </Group>

                <Space h="xl" />
            </Stack>
        );
    }

    return (
        <Stack pt="lg" gap="lg">
            <Title order={2} fw={400} c="white">
                Your First Course
            </Title>

            <Text>
                To build a Couse, simply start talking to your instructor about
                what you want to learn. You’ll be able to watch the general
                details of the course being built so that you can make any
                corrections before we build the whole course for you.
            </Text>

            <Box bg="dark">
                {!shouldDisplayCourseInfo && (
                    <Text ta="center" p="xl">
                        Your course summary will be displayed here
                    </Text>
                )}

                {shouldDisplayCourseInfo && (
                    <Stack p="lg">
                        <Title order={4} fw={600} c="white">
                            {courseTitle}
                        </Title>

                        <Stack gap={0}>
                            <Title order={5} fw={400} c="white">
                                Course Summary
                            </Title>
                            <Text c="dimmed">{courseDescription}</Text>
                        </Stack>

                        {keyOutcomes.length > 0 && (
                            <Stack gap="xs">
                                <Title order={5} fw={400} c="white">
                                    Key Outcomes
                                </Title>
                                <List>
                                    {keyOutcomes.map((outcome) => (
                                        <List.Item
                                            ml="sm"
                                            c="dimmed"
                                            key={outcome}
                                        >
                                            {outcome}
                                        </List.Item>
                                    ))}
                                </List>
                            </Stack>
                        )}

                        {topics.length > 0 && (
                            <Stack gap="xs">
                                <Title order={5} fw={400} c="white">
                                    Topics
                                </Title>
                                <List>
                                    {topics.map((topic) => (
                                        <List.Item
                                            ml="sm"
                                            c="dimmed"
                                            key={topic}
                                        >
                                            {topic}
                                        </List.Item>
                                    ))}
                                </List>
                            </Stack>
                        )}
                    </Stack>
                )}
            </Box>
        </Stack>
    );
};
