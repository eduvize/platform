import { Text, Card, Box, Flex } from "@mantine/core";
import { CourseListingDto } from "@models/dto";
import classes from "./CourseListing.module.css";
import { IconCircleCheckFilled, IconPlus } from "@tabler/icons-react";

type CourseListingProps =
    | (Partial<CourseListingDto> & { is_new: true; onClick: () => void })
    | (CourseListingDto & { is_new?: false; onClick: () => void });

export const CourseListing = ({
    is_new,
    title,
    cover_image_url,
    progress,
    is_generating,
    onClick,
}: CourseListingProps) => {
    return (
        <Box pos="relative">
            <Card
                pos="relative"
                withBorder
                className={classes.courseCard}
                bg={
                    is_new
                        ? undefined
                        : `url(${cover_image_url}) center / cover`
                }
                onClick={onClick}
                styles={{
                    root: {
                        padding: 0,
                    },
                }}
            >
                {!is_new && progress === 100 && (
                    <Box pos="absolute" top={8} right={16} w={24} h={24}>
                        <Box
                            pos="absolute"
                            top={8}
                            left={10}
                            bg="white"
                            w={12}
                            h={12}
                        ></Box>
                        <IconCircleCheckFilled
                            color="#51cf66"
                            size={32}
                            style={{ position: "absolute" }}
                        />
                    </Box>
                )}

                {!is_new && (
                    <Flex h="100%" align="flex-end">
                        <Box bg="rgba(0, 0, 0, 0.6)" p="xs">
                            <Text size="lg" c="white" fw={700}>
                                {title}
                            </Text>

                            <Text
                                size="sm"
                                fw={600}
                                c={
                                    !is_generating && progress >= 100
                                        ? "green"
                                        : "blue"
                                }
                            >
                                {is_generating
                                    ? `${progress}% generated`
                                    : `${progress}% complete`}
                            </Text>
                        </Box>
                    </Flex>
                )}

                {is_new && (
                    <Flex w="100%" h="100%" align="center" justify="center">
                        <IconPlus color="white" size={48} />
                    </Flex>
                )}
            </Card>
        </Box>
    );
};
