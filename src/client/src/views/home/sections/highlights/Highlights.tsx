import { Container, Grid, Title, Text, Image, Space, Box } from "@mantine/core";
import handsOnImage from "./handson.png";
import personalizedImage from "./personalized.png";
import { useMediaQuery } from "@mantine/hooks";

interface SectionProps {
    title: string;
    description: string;
    image?: string;
}

export const Highlights = () => {
    const gridColStyle = { border: "1px solid #424242", borderRadius: "4px" };
    const isMobile = useMediaQuery("(max-width: 768px)");

    const Section = ({ title, description, image }: SectionProps) => {
        return (
            <Grid.Col span={isMobile ? 12 : 6}>
                <Box px="xl" style={gridColStyle} h="100%">
                    <Title order={3} fw="600" c="#8DCAFF" mt="md" mb="xs">
                        {title}
                    </Title>

                    <Text c="gray" size="sm">
                        {description}
                    </Text>

                    {image && (
                        <>
                            <Image
                                src={image}
                                alt={title}
                                mt="xl"
                                style={{ border: "1px solid #424242" }}
                            />

                            <Space h="xl" />
                        </>
                    )}
                </Box>
            </Grid.Col>
        );
    };

    return (
        <Container size="xl">
            <Grid gutter={16}>
                <Section
                    title="Learn by Doing"
                    description="Theory is important, but practice is where the magic happens. Eduvize emphasizes hands-on exercises and real-world projects, allowing you to apply what you've learned immediately. Get instant feedback and track your progress as you code, with our AI tutor guiding you every step of the way."
                    image={handsOnImage}
                />

                <Section
                    title="Personalized to Match Your Skills and Goals"
                    description="Eduvize gets to know you—your strengths, goals, and interests. It adapts to your unique learning style, offering customized content that’s tailored to accelerate your growth as a developer. Whether you're mastering new technologies or refining your skills, we ensure you're always learning what’s most relevant to you."
                    image={personalizedImage}
                />
            </Grid>
        </Container>
    );
};
