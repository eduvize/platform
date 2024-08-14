import {
    Badge,
    Group,
    Title,
    Text,
    Card,
    SimpleGrid,
    Container,
    rem,
    useMantineTheme,
    Center,
    Space,
} from "@mantine/core";
import {
    IconUser,
    IconDirections,
    IconMapQuestion,
    IconCloudComputing,
    IconBooks,
    IconMoodDollar,
} from "@tabler/icons-react";
import classes from "./Features.module.css";

const mockdata = [
    {
        title: "Tailored to you",
        description: `
Once you fill out your comprehensive profile, we'll be able to generate your own personal tutor that will help design and guide you through courses that are tailored to your exact needs. There's no cookie-cutter approach here.
`,
        icon: IconUser,
    },
    {
        title: "Beyond Theory",
        description: `
Learning through tutorials and books is a good start, but true mastery comes from hands-on experience.
We provide practical exercises and real-world projects that reinforce your understanding and help you apply what you've learned.
`,
        icon: IconBooks,
    },
    {
        title: "More Than Just Code",
        description: `
    Being a developer is about more than writing code. 
    Success in the industry requires mastering a variety of frameworks, tools, and methodologies.
    Our platform helps you integrate these concepts, ensuring you become a well-rounded professional.
    `,
        icon: IconDirections,
    },
    {
        title: "Personalized Learning Path",
        description: `
    Navigating the journey of learning to code can be daunting, especially when deciding what to tackle next.
    Eduvize simplifies this process by recommending the next steps based on your progress.
    Just mastered React? We'll guide you towards Redux to build on your skills!
    `,
        icon: IconMapQuestion,
    },
    {
        title: "Hands-On Practice",
        description: `
    The most effective way to learn is through action. 
    We'll provide you with a web-based environment where you can apply concepts in real-time, guided by your AI tutor.
    Whether you're writing and testing code, designing a webpage, or setting up a server, we've got you covered.
    `,
        icon: IconCloudComputing,
    },
    {
        title: "Boost Your Job Prospects",
        description: `
    We understand that many use our platform to land their next job.
    We'll support you by helping you build a portfolio of impressive projects to showcase to potential employers.
    Plus, we can generate a tailored curriculum based on the jobs you're targeting.
    Share the job posting with us, and we'll guide you toward success.
    `,
        icon: IconMoodDollar,
    },
];

export function Features() {
    const theme = useMantineTheme();
    const features = mockdata.map((feature) => (
        <Card
            key={feature.title}
            shadow="md"
            radius="md"
            className={classes.card}
            padding="xl"
        >
            <feature.icon
                style={{ width: rem(50), height: rem(50) }}
                stroke={2}
                color={theme.colors.blue[6]}
            />
            <Text fz="lg" fw={500} className={classes.cardTitle} mt="md">
                {feature.title}
            </Text>
            <Text fz="sm" c="dimmed" mt="sm">
                {feature.description}
            </Text>
        </Card>
    ));

    return (
        <Container size="lg" py="xl">
            <Space h="xl" />

            <Group justify="center">
                <Badge variant="filled" size="lg">
                    Your journey starts here
                </Badge>
            </Group>

            <Space h="lg" />

            <Title order={2} ta="center" mt="sm" size={32}>
                Discover the Power of Eduvize
            </Title>

            <Center>
                <Text
                    c="dimmed"
                    className={classes.description}
                    ta="center"
                    mt="md"
                    size="sm"
                >
                    Our suite of tailored tools is designed to elevate your
                    development skills, all in one place. Whether you're looking
                    to advance your career or land a new job, Eduvize has you
                    covered.
                </Text>
            </Center>

            <SimpleGrid cols={{ base: 1, md: 3 }} spacing="xl" mt={50}>
                {features}
            </SimpleGrid>
        </Container>
    );
}
