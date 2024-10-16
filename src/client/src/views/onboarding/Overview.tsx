import {
    Box,
    Stack,
    Title,
    Text,
    Space,
    Divider,
    Group,
    Button,
} from "@mantine/core";

interface OverviewProps {
    onNext: () => void;
}

export const Overview = ({ onNext }: OverviewProps) => {
    return (
        <Box pt="lg">
            <Stack>
                <Title order={2} fw={400} c="white">
                    Overview
                </Title>

                <Title order={4} fw={400} c="white">
                    The Navigator
                </Title>

                <Text>
                    The first thing you’ll notice is the{" "}
                    <span style={{ color: "#51CF66", fontWeight: "bold" }}>
                        Navigator
                    </span>{" "}
                    on the left. This outlines the <b>Lessons</b> in each{" "}
                    <b>Module</b>.
                    <br />
                    Depending on the size and complexity of the <b>Course</b>,
                    it’s likely that your Course will consist of multiple
                    modules. This will all be outlined in your <b>Syllabus</b>.{" "}
                    <br /> <br />
                    In this case: <br />
                    Your Course is <b>Welcome to Eduvize</b>.<br />
                    Your Module is <b>Get Ready for Your First Course</b>
                    <br />
                    This Lesson is <b>Overview</b>
                    <br /> <br />
                    The Navigator will be wil you no matter where you are in
                    your Course, to help you if you want to go back, explore, or
                    move on to another Course.
                </Text>

                <Space />

                <Title order={4} fw={400} c="white">
                    Your Profile
                </Title>

                <Text>
                    The more we know about you and your work, the better your
                    experience will be. We’ll start by filling out a basic
                    profile, and your Instructor will ask you more questions to
                    help tailor your courses to your specific styles. You can
                    update this at any time by talking to your Instructor, or by
                    clicking on <b>Profile</b> on the top right.
                </Text>

                <Space />

                <Title order={4} fw={400} c="white">
                    The Instructor
                </Title>

                <Text>
                    Your Instructor will be your AI Companion through your
                    Courses. They’ll help you summarize content, work through
                    problems, and be your overall guide. You’ll learn more about
                    your instructor in the <b>Meet Your Instructor</b> Lesson.
                </Text>

                <Space />

                <Divider />

                <Group>
                    <Button onClick={onNext}>Next Lesson</Button>
                </Group>

                <Space h="lg" />
            </Stack>
        </Box>
    );
};
