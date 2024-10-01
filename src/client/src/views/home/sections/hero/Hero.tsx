import {
    Container,
    Text,
    Button,
    Group,
    Space,
    Center,
    Image,
    Title,
} from "@mantine/core";
import { GithubIcon } from "@mantinex/dev-icons";
import classes from "./Hero.module.css";
import logo from "../../logo.png";
import { Link } from "react-router-dom";
import bg from "./background.png";
import { useMediaQuery } from "@mantine/hooks";

export function Hero() {
    const isMobile = useMediaQuery("(max-width: 768px)");

    return (
        <div className={classes.wrapper}>
            <Image
                pos="absolute"
                left={0}
                top={0}
                src={bg}
                opacity={0.1}
                h="100%"
                w="100%"
            />
            <Container size={800} className={classes.inner}>
                <Center>
                    <img
                        src={logo}
                        alt="Eduvize Logo"
                        className={classes.logo}
                        width={isMobile ? "90%" : "533px"}
                    />
                </Center>
                <Space h="xl" />
                <Center>
                    <Title
                        order={1}
                        component="span"
                        c="white"
                        tt="uppercase"
                        ta="center"
                        size={isMobile ? 28 : undefined}
                    >
                        <b style={{ color: "#8dcaff" }}>Supercharge</b> your dev
                        skills using A{" "}
                        <b
                            style={{
                                color: "var(--mantine-color-green-5",
                            }}
                        >
                            Personal AI Instructor
                        </b>
                    </Title>
                </Center>

                <Space h="lg" />
                <Text className={classes.description} c="white">
                    Learning new software development skills can be challenging,
                    but staying ahead is crucial. With Eduvize, powered by
                    cutting-edge AI, you can quickly master the latest
                    technologies through tailored courses, exercises, and
                    projects that match your unique needs.
                </Text>
                <Group className={classes.controls} justify="center">
                    <Link to="/auth">
                        <Button
                            size="xl"
                            className={classes.button}
                            variant="gradient"
                            gradient={{ from: "blue", to: "cyan" }}
                        >
                            Get Started
                        </Button>
                    </Link>
                </Group>
            </Container>
        </div>
    );
}
