import { Link } from "react-router-dom";
import image from "./image.svg";
import { Text, Title, Button, Image } from "@mantine/core";
import classes from "./SetupCta.module.css";

export function SetupCta() {
    return (
        <div className={classes.wrapper}>
            <div className={classes.body}>
                <Title className={classes.title}>Welcome to the platform</Title>
                <Text fw={500} fz="lg" mb={5}>
                    It's time to set up your profile
                </Text>
                <Text fz="sm" c="dimmed">
                    In order to personalize your experience and get started with
                    your first course, we need some information from you. Don't
                    worry, we won't share this information with anyone - it's
                    just for us to fine-tune our AI instructors to best suit
                    your learning style.
                </Text>

                <div className={classes.controls}>
                    <Link to="/dashboard/profile">
                        <Button size="lg" className={classes.control}>
                            Get Started
                        </Button>
                    </Link>
                </div>
            </div>

            <Image src={image} className={classes.image} />
        </div>
    );
}
