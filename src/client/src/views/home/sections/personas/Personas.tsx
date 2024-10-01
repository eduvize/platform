import {
    Avatar,
    Center,
    Group,
    Radio,
    Stack,
    Title,
    Text,
    Container,
} from "@mantine/core";
import beginnerImage from "./headshots/beginner.png";
import consultantImage from "./headshots/consultant.png";
import educatorImage from "./headshots/educator.png";
import leaderImage from "./headshots/leader.png";
import switcherImage from "./headshots/switcher.png";
import { useState } from "react";
import { useMediaQuery } from "@mantine/hooks";

const personas = [
    {
        image: leaderImage,
        title: "Leader",
        description: `Eduvize keeps you informed with high-level insights and trends in development, while still offering hands-on opportunities to sharpen your technical skills when you need them. We help you bridge the gap between leadership and technical fluency, making it easier to guide your team with confidence and communicate complex ideas clearly.`,
    },
    {
        image: switcherImage,
        title: "Job Switcher",
        description: `Eduvize will help you make the leap. Our platform tailors learning paths to your goals, offering courses that get you up to speed on the latest technologies and practices. We focus on practical, project-based learning, so you can build a portfolio that showcases your new skills and sets you up for success in your next role.`,
    },
    {
        image: consultantImage,
        title: "Consultant",
        description: `Eduvize offers bite-sized lessons and hands-on projects that fit seamlessly into your busy schedule. Whether you're looking to learn a new skill quickly or dive deep into a new area, our personalized courses ensure you’re always one step ahead of client expectations. Stay sharp and adaptable with Eduvize.`,
    },
    {
        image: educatorImage,
        title: "Educator",
        description: `Eduvize helps you stay on top of the latest trends and technologies, offering tools and resources you can use both to improve your own skills and to enrich your teaching. With access to our practical exercises and projects, you can ensure your students are not only learning theory but also gaining the hands-on experience they need to succeed.`,
    },
    {
        image: beginnerImage,
        title: "Beginner",
        description: `Eduvize is designed with beginners in mind. Our platform breaks complex topics down into simple, easy-to-follow lessons. You'll get personalized course recommendations based on your interests and goals, hands-on exercises to help you practice what you learn, and automated feedback to keep you on track. We make coding approachable, one step at a time.`,
    },
];

export const Personas = () => {
    const isMobile = useMediaQuery("(max-width: 768px)");
    const [selectedIndex, setSelectedIndex] = useState(0);
    const persona = personas[selectedIndex];

    return (
        <Stack py="lg" gap="xl">
            <Title order={2} c="white" ta="center">
                How can Eduvize help you?
            </Title>

            <Group justify="center" gap="xl" p={isMobile ? "lg" : 0}>
                {personas.map(({ image, title, description }) => (
                    <Radio
                        key={title}
                        label={title}
                        variant="outline"
                        size="lg"
                        value={title}
                        checked={title === persona.title}
                        onChange={() =>
                            setSelectedIndex(
                                personas.findIndex((p) => p.title === title)
                            )
                        }
                        styles={{
                            radio: {
                                border: "2px solid #1479B2",
                                background: "transparent",
                            },
                        }}
                    />
                ))}
            </Group>

            <Container size="sm">
                <Center>
                    <Stack>
                        <Center>
                            <Avatar src={persona.image} size={128} />
                        </Center>

                        <Title order={2} ta="center" c="#8DCAFF">
                            {persona.title}
                        </Title>

                        <Text size="md" c="gray" ta="center">
                            {persona.description}
                        </Text>
                    </Stack>
                </Center>
            </Container>
        </Stack>
    );
};
