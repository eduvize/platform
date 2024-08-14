import { Container, Text, Button, Group, Space } from "@mantine/core";
import { GithubIcon } from "@mantinex/dev-icons";
import classes from "./Hero.module.css";
import logo from "../../logo.png";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";

export function Hero() {
    const [underline, setUnderline] = useState(false);

    useEffect(() => {
        setTimeout(() => {
            setUnderline(true);
        }, 700);
    }, []);

    return (
        <div className={classes.wrapper}>
            <Container size={750} className={classes.inner}>
                <img src={logo} alt="Eduvize Logo" className={classes.logo} />

                <Space h="lg" />

                <h1 className={classes.title}>
                    <Text
                        component="span"
                        variant="gradient"
                        gradient={{ from: "blue", to: "cyan" }}
                        inherit
                        className={classes.glowing}
                    >
                        Supercharge
                    </Text>{" "}
                    your dev skills using{" "}
                    <Text
                        component="span"
                        variant="gradient"
                        gradient={{ from: "orange", to: "red" }}
                        inherit
                        className={`${classes.underline}${
                            underline ? ` ${classes.underlineAnimated}` : ""
                        }`}
                    >
                        A Personal AI Tutor
                    </Text>
                </h1>

                <Space h="lg" />

                <Text className={classes.description} color="dimmed">
                    Learning new software development skills can be challenging,
                    but staying ahead is crucial. With Eduvize, powered by
                    cutting-edge AI, you can quickly master the latest
                    technologies through tailored courses, exercises, and
                    projects that match <b>your</b> unique needs.
                </Text>

                <Group className={classes.controls}>
                    <Link to="/auth">
                        <Button
                            size="xl"
                            className={classes.button}
                            variant="gradient"
                            gradient={{ from: "blue", to: "cyan" }}
                        >
                            Get started for free
                        </Button>
                    </Link>

                    <Button
                        component="a"
                        href="https://github.com/cameron5906/eduvize-ai"
                        size="xl"
                        variant="default"
                        className={classes.button}
                        leftSection={<GithubIcon size={20} />}
                    >
                        Contribute
                    </Button>
                </Group>
            </Container>
        </div>
    );
}
