import {
    BackgroundImage,
    Box,
    Card,
    Container,
    Stack,
    Title,
    Text,
    Divider,
    Button,
    Group,
    Space,
} from "@mantine/core";
import background from "./background.png";

interface WelcomeProps {
    onGetStarted: () => void;
}

export const Welcome = ({ onGetStarted }: WelcomeProps) => {
    return (
        <Container size="md">
            <Stack>
                <Box pos="relative" h={164}>
                    <BackgroundImage src={background} opacity={0.2} h={164} />
                    <Title
                        pos="absolute"
                        order={2}
                        c="white"
                        top="50%"
                        mt={-16}
                        fw={400}
                        ta="center"
                        w="100%"
                        style={{ fontSize: 32 }}
                    >
                        Welcome to Eduvize!
                    </Title>
                </Box>

                <Card withBorder p="xl">
                    <Text c="white">
                        Before we get started on your first course, we’re going
                        to show you around, and get to know you a little bit.
                        Filling out your profile will be just like taking a
                        class, and you’ll even get to meet your instructor.
                    </Text>
                </Card>

                <Card withBorder>
                    <Stack px="xl">
                        <Space h="lg" />
                        <Title order={4} c="white">
                            Get Ready for your First Course
                        </Title>
                        <Text>
                            Here we’ll fill out your profile. This way we can
                            tailor your courses to your level of expertise and
                            experience. From Beginner to Expert, we’ll provide a
                            challenge without completely overwhelming you.
                        </Text>

                        <Divider />

                        <Group>
                            <Button onClick={onGetStarted}>Get Started</Button>
                        </Group>
                        <Space h="lg" />
                    </Stack>
                </Card>
            </Stack>
        </Container>
    );
};
