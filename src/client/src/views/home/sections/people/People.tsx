import {
    Center,
    Grid,
    Title,
    Text,
    Container,
    Avatar,
    Flex,
    Stack,
} from "@mantine/core";
import { Carousel } from "@mantine/carousel";
import leader from "./lead.png";
import beginner from "./beginner.png";
import educator from "./educator.png";
import consultant from "./consultant.png";
import switcher from "./switcher.png";
import student from "./student.png";

interface PersonaProps {
    name: string;
    description: string;
    image: string;
}

export const People = () => {
    const Persona = ({ name, description, image }: PersonaProps) => {
        return (
            <Carousel.Slide px="xl">
                <Center mb="xs">
                    <Avatar src={image} size="xl" />
                </Center>
                <Title size={28} fw="200" ff="Roboto" c="blue" ta="center">
                    {name}
                </Title>

                <Text mt="md" px="xl" ta="center">
                    {description}
                </Text>
            </Carousel.Slide>
        );
    };

    return (
        <Container size="xl">
            <Center>
                <Stack>
                    <Center>
                        <Title ff="Roboto" c="white" mb="xl">
                            Who Are You?
                        </Title>
                    </Center>

                    <Container size="md">
                        <Carousel
                            slideSize="100%"
                            height={350}
                            slideGap={0}
                            withIndicators
                        >
                            <Persona
                                name="A Leader"
                                description="Eduvize keeps you informed with high-level insights and trends in development, while still offering hands-on opportunities to sharpen your technical skills when you need them. We help you bridge the gap between leadership and technical fluency, making it easier to guide your team with confidence and communicate complex ideas clearly."
                                image={leader}
                            />

                            <Persona
                                name="Someone wanting a change"
                                description="Eduvize will help you make the leap. Our platform tailors learning paths to your goals, offering courses that get you up to speed on the latest technologies and practices. We focus on practical, project-based learning, so you can build a portfolio that showcases your new skills and sets you up for success in your next role."
                                image={switcher}
                            />

                            <Persona
                                name="A Contractor"
                                description="Eduvize offers bite-sized lessons and hands-on projects that fit seamlessly into your busy schedule. Whether you're looking to learn a new skill quickly or dive deep into a new area, our personalized courses ensure you’re always one step ahead of client expectations. Stay sharp and adaptable with Eduvize."
                                image={consultant}
                            />

                            <Persona
                                name="An Educator"
                                description="Eduvize helps you stay on top of the latest trends and technologies, offering tools and resources you can use both to improve your own skills and to enrich your teaching. With access to our practical exercises and projects, you can ensure your students are not only learning theory but also gaining the hands-on experience they need to succeed."
                                image={educator}
                            />

                            <Persona
                                name="A Beginner"
                                description="Eduvize is designed with beginners in mind. Our platform breaks complex topics down into simple, easy-to-follow lessons. You'll get personalized course recommendations based on your interests and goals, hands-on exercises to help you practice what you learn, and automated feedback to keep you on track. We make coding approachable, one step at a time."
                                image={beginner}
                            />

                            <Persona
                                name="A Student"
                                description="Eduvize complements your formal education by providing hands-on, project-based learning. Our platform helps you apply the concepts you’re learning in the classroom to real-world scenarios, so you can build a portfolio that stands out to future employers. We focus on practical skills that will help you thrive in your career."
                                image={student}
                            />
                        </Carousel>
                    </Container>
                </Stack>
            </Center>
        </Container>
    );
};
