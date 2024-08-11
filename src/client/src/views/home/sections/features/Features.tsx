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
Everything you do on this site is entirely based around you and your needs. 
It's like having a personal tutor, but without the cost or anxiety!
Your AI tutor will get to know you and will be able to leverage concepts you already know to help you learn new ones
`,
        icon: IconUser,
    },
    {
        title: "More than reading",
        description: `
Scouring the Internet for tutorials and reading books can get you so far, but it's not the most effective way to learn.
We'll help you learn by doing, with hands-on exercises and projects that will help you retain the information better.
`,
        icon: IconBooks,
    },
    {
        title: "More than just languages",
        description: `
There's a lot more to being a developer than just knowing how to code.
The industry is filled with different frameworks, tools, and methodologies that you need to know to be successful.
Our platform will help you marry these concepts together to ensure you're well-rounded
`,
        icon: IconDirections,
    },
    {
        title: 'No more "what do I learn next?"',
        description: `
One of the most challenging parts of learning to code is figuring out what to learn next.
Eduvize will help take care of that for you by recommending follow-up topics based on what you've already learned.
Did you just learn more about React? We'll suggest learning Redux next!
`,
        icon: IconMapQuestion,
    },
    {
        title: "Hands-on Learning",
        description: `
The best way to learn is by doing. We'll set you up with a web-based environment where you can practice all of these concepts in real-time with your AI tutor by your side.
Whether its writing and testing code, learning how to design a webpage, or even setting up a server - we've got you covered
`,
        icon: IconCloudComputing,
    },
    {
        title: "Get that next job",
        description: `
We know that a lot of people use our platform to help them get that next job.
We'll help you by building a portfolio of projects that you can show off to potential employers, and even generate a curriculum based on jobs you're interested in.
Give us the posting, and we'll help you get there
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
            <Group justify="center">
                <Badge variant="filled" size="lg">
                    Everything is tailored to you
                </Badge>
            </Group>

            <Title order={2} className={classes.title} ta="center" mt="sm">
                Learn more about what Eduvize has to offer
            </Title>

            <Center>
                <Text
                    c="dimmed"
                    className={classes.description}
                    ta="center"
                    mt="md"
                >
                    Our suite of tools is designed to make leveling up your
                    development abilities without having to go anywhere else.
                </Text>
            </Center>

            <SimpleGrid cols={{ base: 1, md: 3 }} spacing="xl" mt={50}>
                {features}
            </SimpleGrid>
        </Container>
    );
}
