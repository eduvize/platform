import { BackgroundImage, Container, Flex, Space, Title } from "@mantine/core";
import { IconPlayerPlay } from "@tabler/icons-react";

export const Video = () => {
    return (
        <Container size="lg">
            <Title
                c="white"
                order={2}
                ta="center"
                mt="sm"
                tt="uppercase"
                size={32}
            >
                Discover the Power of Eduvize
            </Title>

            <Space h="xl" />

            <BackgroundImage
                src={""}
                bg="dark"
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
