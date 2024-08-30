import cx from "clsx";
import { Title, Text, Container, Button, Overlay, Stack } from "@mantine/core";
import classes from "./Hero.module.css";
import { useCourse } from "@context/course/hooks";

export const Hero = () => {
    const { title, description, cover_image_url } = useCourse();

    return (
        <div
            className={classes.wrapper}
            style={{
                backgroundImage: `url(${cover_image_url})`,
            }}
        >
            <Overlay color="#000" opacity={0.65} zIndex={1} />

            <div className={classes.inner}>
                <Stack gap="xl" px="xl">
                    <Title className={classes.title}>{title}</Title>
                </Stack>
            </div>
        </div>
    );
};
