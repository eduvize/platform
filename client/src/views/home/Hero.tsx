import { Container, Text, Button, Group, Space } from "@mantine/core";
import { GithubIcon } from "@mantinex/dev-icons";
import classes from "./Hero.module.css";
import logo from "./logo.png";
import { Link } from "react-router-dom";

export function Hero() {
    return (
        <div className={classes.wrapper}>
            <Container size={700} className={classes.inner}>
                <img src={logo} alt="Eduvize Logo" className={classes.logo} />

                <Space h="lg" />

                <h1 className={classes.title}>
                    <Text
                        component="span"
                        variant="gradient"
                        gradient={{ from: "blue", to: "cyan" }}
                        inherit
                    >
                        Supercharge
                    </Text>{" "}
                    your dev skills using{" "}
                    <Text
                        component="span"
                        variant="gradient"
                        gradient={{ from: "orange", to: "red" }}
                        inherit
                    >
                        AI curriculums
                    </Text>
                </h1>

                <Space h="lg" />

                <Text className={classes.description} color="dimmed">
                    Learning new software development skills can be challenging
                    and time-consuming, let alone keeping up with the latest
                    trends once you're already a professional.
                </Text>

                <Space h="sm" />

                <Text className={classes.description} color="dimmed">
                    Using the latest in AI technology, Eduvize can help you
                    learn new skills by generating courses, exercises, and
                    projects tailored to <b>your</b> exact needs.
                </Text>

                <Group className={classes.controls}>
                    <Link to="/auth">
                        <Button
                            size="xl"
                            className={classes.control}
                            variant="gradient"
                            gradient={{ from: "blue", to: "cyan" }}
                        >
                            Get started for free
                        </Button>
                    </Link>

                    <Button
                        component="a"
                        href="https://github.com/mantinedev/mantine"
                        size="xl"
                        variant="default"
                        className={classes.control}
                        leftSection={<GithubIcon size={20} />}
                    >
                        Contribute
                    </Button>
                </Group>
            </Container>
        </div>
    );
}
