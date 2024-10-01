import {
    Container,
    Text,
    Button,
    Group,
    Space,
    Center,
    Image,
} from "@mantine/core";
import { GithubIcon } from "@mantinex/dev-icons";
import classes from "./Hero.module.css";
import logo from "../../logo.png";
import { Link } from "react-router-dom";
import bg from "./background.png";

export function Hero() {
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
                    />
                </Center>

                <Space h="xl" />

                <h1 className={classes.title}>
                    <Text
                        component="span"
                        c="#8dcaff"
                        inherit
                        className={classes.glowing}
                    >
                        Supercharge
                    </Text>{" "}
                    your dev skills using A{" "}
                    <Text component="span" c="green" inherit>
                        Personal AI Instructor
                    </Text>
                </h1>

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
