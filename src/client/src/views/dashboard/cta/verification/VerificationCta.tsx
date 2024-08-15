import { Link } from "react-router-dom";
import image from "./image.svg";
import { Text, Title, Button, Image } from "@mantine/core";
import classes from "./VerificationCta.module.css";

export function VerificationCta() {
    return (
        <div className={classes.wrapper}>
            <div className={classes.body}>
                <Title className={classes.title}>Awaiting Verification</Title>
                <Text fw={500} fz="lg" mb={5}>
                    Check your email for a message from us
                </Text>
                <Text fz="sm" c="dimmed">
                    We sent you an email with a link to verify your account.
                    Please check your inbox and click on it so you can start
                    using the platform.
                </Text>

                <div className={classes.controls}>
                    <Link to="/dashboard/profile">
                        <Button
                            pl={0}
                            size="sm"
                            variant="transparent"
                            className={classes.control}
                        >
                            Didn't get it? Click here to resend
                        </Button>
                    </Link>
                </div>
            </div>

            <Image src={image} className={classes.image} />
        </div>
    );
}
