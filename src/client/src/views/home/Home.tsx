import {
    Group,
    Title,
    Text,
    Container,
    Divider,
    Space,
    Stack,
    Button,
} from "@mantine/core";
import { Footer } from "./Footer";
import { Features, Hero, Highlights, Instructors, Personas } from "./sections";
import { useNavigate } from "react-router-dom";
import { useMediaQuery } from "@mantine/hooks";

export function Home() {
    const navigate = useNavigate();
    const isMobile = useMediaQuery("(max-width: 768px)");

    return (
        <>
            <Hero />

            <Container size="lg">
                <Group
                    wrap={isMobile ? "wrap" : "nowrap"}
                    justify="center"
                    py="xl"
                >
                    <Title
                        c="white"
                        order={2}
                        miw={390}
                        ta={isMobile ? "center" : undefined}
                    >
                        Built to Empower Developers
                    </Title>
                    <Text
                        c="white"
                        size="sm"
                        p={isMobile ? "md" : 0}
                        ta={isMobile ? "center" : undefined}
                    >
                        Our suite of tailored tools is designed to elevate your
                        development skills, all in one place. Whether you're
                        looking to advance your career or land a new job,
                        Eduvize has you covered.
                    </Text>
                </Group>
            </Container>

            <Divider c="dark" />
            <Personas />
            <Space h="xl" />
            <Space h="xl" />
            <Highlights />
            <Space h="xl" />
            <Instructors />
            <Features />

            <Space h="xl" />

            <Stack p={isMobile ? "xl" : 0}>
                <Title order={2} c="white" ta="center">
                    Are you ready to take your skills to the next level?
                </Title>

                <Group justify="center">
                    <Button
                        bg="blue"
                        onClick={() => {
                            navigate("/auth");
                        }}
                    >
                        Get Started
                    </Button>
                </Group>
            </Stack>

            <Space h={120} />

            <Footer />
        </>
    );
}
