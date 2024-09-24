import {
    Center,
    Grid,
    Title,
    Text,
    Container,
    Group,
    Box,
    Space,
    Card,
} from "@mantine/core";
import { Carousel } from "@mantine/carousel";

export const People = () => {
    return (
        <Container size="xl">
            <Center>
                <Grid mt="lg">
                    <Grid.Col span={12}>
                        <Center>
                            <Title ff="Roboto" c="white" mb="xl">
                                Who Are You?
                            </Title>
                        </Center>
                    </Grid.Col>

                    <Grid.Col span={12}>
                        <Carousel slideSize="50%" height={200} slideGap="xl">
                            <Carousel.Slide>
                                <Title size={28} fw="200" ff="Roboto" c="blue">
                                    A Leader
                                </Title>

                                <Text>
                                    You're managing a team of developers, and it
                                    feels like you're always juggling both the
                                    big-picture vision and the details. You need
                                    to stay updated on new technologies, but you
                                    rarely have time to dig into the weeds or
                                    work directly with code. On top of that,
                                    communicating technical concepts to
                                    non-technical stakeholders can be a
                                    challenge.
                                </Text>

                                <Text mt="md">
                                    Eduvize keeps you informed with high-level
                                    insights and trends in development, while
                                    still offering hands-on opportunities to
                                    sharpen your technical skills when you need
                                    them. We help you bridge the gap between
                                    leadership and technical fluency, making it
                                    easier to guide your team with confidence
                                    and communicate complex ideas clearly.
                                </Text>
                            </Carousel.Slide>

                            <Carousel.Slide>
                                <Title size={28} fw="200" ff="Roboto" c="blue">
                                    Someone wanting a change
                                </Title>
                                <Text>
                                    You've been in your current role for a
                                    while, but you're feeling stagnant. Maybe
                                    you're in a non-technical position and want
                                    to shift into development, or you're a
                                    developer looking to expand your skills into
                                    a new area. Either way, you're ready for a
                                    change but unsure where to start.
                                </Text>

                                <Text mt="md">
                                    Eduvize will help you make the leap. Our
                                    platform tailors learning paths to your
                                    goals, offering courses that get you up to
                                    speed on the latest technologies and
                                    practices. We focus on practical,
                                    project-based learning, so you can build a
                                    portfolio that showcases your new skills and
                                    sets you up for success in your next role.
                                </Text>
                            </Carousel.Slide>

                            <Carousel.Slide>
                                <Title size={28} fw="200" ff="Roboto" c="blue">
                                    A Contractor
                                </Title>

                                <Text>
                                    You’re constantly moving from project to
                                    project, each with its own unique set of
                                    requirements. Keeping up with the latest
                                    tools and trends is critical to staying
                                    competitive, but you need a flexible
                                    learning schedule that fits around client
                                    deadlines.
                                </Text>

                                <Text mt="md">
                                    Eduvize offers bite-sized lessons and
                                    hands-on projects that fit seamlessly into
                                    your busy schedule. Whether you're looking
                                    to learn a new skill quickly or dive deep
                                    into a new area, our personalized courses
                                    ensure you’re always one step ahead of
                                    client expectations. Stay sharp and
                                    adaptable with Eduvize.
                                </Text>
                            </Carousel.Slide>

                            <Carousel.Slide>
                                <Title size={28} fw="200" ff="Roboto" c="blue">
                                    An Educator
                                </Title>
                                <Text>
                                    You're responsible for teaching the next
                                    generation of developers, but keeping your
                                    curriculum current in an ever-evolving field
                                    is difficult. You want to make sure your
                                    students are learning cutting-edge skills
                                    that will be valuable in the real world, but
                                    you also need to balance your own
                                    professional growth.
                                </Text>

                                <Text mt="md">
                                    Eduvize helps you stay on top of the latest
                                    trends and technologies, offering tools and
                                    resources you can use both to improve your
                                    own skills and to enrich your teaching. With
                                    access to our practical exercises and
                                    projects, you can ensure your students are
                                    not only learning theory but also gaining
                                    the hands-on experience they need to
                                    succeed.
                                </Text>
                            </Carousel.Slide>

                            <Carousel.Slide>
                                <Title size={28} fw="200" ff="Roboto" c="blue">
                                    A Beginner
                                </Title>
                                <Text>
                                    You're new to coding, and while you're eager
                                    to learn, it all feels a bit overwhelming.
                                    There are so many programming languages,
                                    tools, and frameworks out there, and you're
                                    not sure where to start. You're looking for
                                    guidance and a clear path to becoming a
                                    proficient developer.
                                </Text>

                                <Text mt="md">
                                    Eduvize is designed with beginners in mind.
                                    Our platform breaks complex topics down into
                                    simple, easy-to-follow lessons. You'll get
                                    personalized course recommendations based on
                                    your interests and goals, hands-on exercises
                                    to help you practice what you learn, and
                                    automated feedback to keep you on track. We
                                    make coding approachable, one step at a
                                    time.
                                </Text>
                            </Carousel.Slide>

                            <Carousel.Slide>
                                <Title size={28} fw="200" ff="Roboto" c="blue">
                                    A Student
                                </Title>
                                <Text>
                                    You're currently studying development,
                                    either in school or through another learning
                                    platform, but you feel like you’re not
                                    getting enough practical experience. You
                                    want more than just theory—you want to build
                                    real projects, solve real problems, and be
                                    ready to hit the ground running when you
                                    graduate.
                                </Text>

                                <Text mt="md">
                                    Eduvize complements your formal education by
                                    providing hands-on, project-based learning.
                                    Our platform helps you apply the concepts
                                    you’re learning in the classroom to
                                    real-world scenarios, so you can build a
                                    portfolio that stands out to future
                                    employers. We focus on practical skills that
                                    will help you thrive in your career.
                                </Text>
                            </Carousel.Slide>
                        </Carousel>
                    </Grid.Col>
                </Grid>
            </Center>
        </Container>
    );
};
