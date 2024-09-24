import { Title, Text, Container, Stack, Box, rem } from "@mantine/core";

const data = [
    {
        title: "Learn With Clarity and Confidence",
        description: `
Our platform provides step-by-step courses with clear learning paths, so you never feel overwhelmed or lost. From beginner to advanced, each module is carefully designed to help you build strong foundations, layer by layer, in the most efficient way possible.
`,
    },
    {
        title: "Track Your Growth, Improve Continuously",
        description: `
Understand your progress like never before. With real-time quizzes, projects, and assessments, Eduvize helps you gauge how well you’ve absorbed each topic. Detailed insights and actionable feedback show you exactly where to improve, ensuring you keep growing with every lesson.
`,
    },
    {
        title: "Job-Ready Training for Your Career Goals",
        description: `
Whether you're preparing for a new role or aiming to level up in your current position, Eduvize offers training that’s perfectly aligned with real-world job requirements. We design custom learning paths based on actual job postings, ensuring you acquire the skills employers are actively seeking. Build a standout portfolio with hands-on projects, and boost your interview performance with mock interviews. Eduvize equips you with everything you need to shine and succeed in your next career move.
    `,
    },
];

export function Features() {
    return (
        <Container size="xl" py="xl">
            <Box
                p="xl"
                style={{ border: "1px solid #424242", borderRadius: rem(4) }}
            >
                <Stack>
                    {data.map(({ title, description }) => {
                        return (
                            <>
                                <Title order={3} mt="sm" c="#8DCAFF">
                                    {title}
                                </Title>

                                <Text c="gray" size="sm">
                                    {description}
                                </Text>
                            </>
                        );
                    })}
                </Stack>
            </Box>
        </Container>
    );
}
