import { BackgroundImage, Container, Flex } from "@mantine/core";
import { IconPlayerPlay } from "@tabler/icons-react";
import mock from "./mock.png";

export const Video = () => {
    return (
        <Container size="lg">
            <BackgroundImage
                src={mock}
                style={{
                    backgroundPosition: "0 -600px",
                    border: "1px solid var(--mantine-color-gray-8)",
                    borderRadius: "6px",
                    boxShadow: "0 3px 10px rgba(0, 0, 0, 0.4)",
                }}
            >
                <Flex w="100%" h="500px" justify="center" align="center">
                    <Flex
                        bg="black"
                        w="48px"
                        h="48px"
                        justify="center"
                        align="center"
                        style={{ borderRadius: 99999 }}
                    >
                        <IconPlayerPlay />
                    </Flex>
                </Flex>
            </BackgroundImage>
        </Container>
    );
};
