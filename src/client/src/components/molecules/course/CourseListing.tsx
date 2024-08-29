import { Text, Card, Progress, Box, LoadingOverlay } from "@mantine/core";
import { CourseListingDto } from "@models/dto";
import classes from "./CourseListing.module.css";

interface CourseListingProps extends CourseListingDto {
    onClick: () => void;
}

export const CourseListing = ({
    title,
    cover_image_url,
    is_generating,
    onClick,
}: CourseListingProps) => {
    return (
        <Box pos="relative">
            <LoadingOverlay
                visible={is_generating}
                loaderProps={{
                    type: "dots",
                    color: "lightgray",
                    top: 40,
                }}
                overlayProps={{
                    opacity: 0.8,
                }}
            />

            <Card
                withBorder
                className={classes.courseCard}
                pos="relative"
                w="18vw"
                h="20vh"
                bg={`url(${cover_image_url}) center / cover`}
                onClick={onClick}
            >
                <Text
                    size="xl"
                    c="white"
                    fw={700}
                    style={{
                        textShadow: "0px 0px 8px #000",
                    }}
                >
                    {title}
                </Text>

                {!is_generating && (
                    <Progress
                        pos="absolute"
                        bottom="0"
                        left="0"
                        w="100%"
                        value={50}
                    />
                )}
            </Card>
        </Box>
    );
};
