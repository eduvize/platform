import { Box, Container, Stack, Title, Text, Group } from "@mantine/core";
import { InstructorButton } from "../../../../components/molecules/instructors";
import { useState } from "react";
import image1 from "./headshots/1.png";
import image2 from "./headshots/2.png";
import image3 from "./headshots/3.png";
import image4 from "./headshots/4.png";
import image5 from "./headshots/5.png";
import image6 from "./headshots/6.png";
import image7 from "./headshots/7.png";
import image8 from "./headshots/8.png";

const instructors = [
    {
        src: image1,
        sample: `Alright, let's get excited about making this peanut butter and jelly sandwich! First, grab two slices of bread—whatever kind you like, you’re already doing amazing! 🎉 Now spread that peanut butter on one slice—no need to be perfect, just go for it! Feeling good? Awesome! Now grab the jelly and spread it on the other slice—any amount you want is great. Now put those slices together, and boom! You've got yourself a delicious PB&J! You totally nailed it! High five!`,
    },
    {
        src: image2,
        sample: `Let's make this sandwich step-by-step. First, take two slices of bread and place them on your workspace, ensuring they're aligned. Now, measure exactly one tablespoon of peanut butter and spread it evenly over one slice of bread. Repeat with one tablespoon of jelly on the other slice, ensuring an even coat from edge to edge. Press the slices together carefully, ensuring no misalignment. Once assembled, cut the sandwich diagonally into two neat halves. You're done. Proceed to clean up and organize your workspace.`,
    },
    {
        src: image3,
        sample: `Alright, let’s make a peanut butter and jelly sandwich together. Start by picking out two slices of bread—any type works, so choose what you love. Great! Now, spread a nice, even layer of peanut butter on one slice, and remember, it doesn’t have to be perfect. Now do the same with jelly on the other slice, using as much or as little as you like. Wonderful work! Now, press the two slices together gently and cut the sandwich in half if you prefer smaller bites. There you go—your perfect PB&J is ready! Fantastic job, you should feel proud!`,
    },
    {
        src: image4,
        sample: `Okay, let’s make this sandwich at your own pace. First, grab any two slices of bread you have on hand. Nice choice. Now, take some peanut butter and spread it across one slice—doesn’t matter how much, just go with what feels right. Then, grab some jelly and spread that on the other slice, again, no need for precision. When you’re ready, just press the slices together. That’s it! You can cut it if you want or leave it whole. Either way, you’ve made your sandwich, and it’s perfect for you!`,
    },
    {
        src: image5,
        sample: `Get two slices of bread, peanut butter, and jelly. Put peanut butter on one slice, jelly on the other. Press them together. Done.`,
    },
    {
        src: image6,
        sample: `This is going to be AMAZING! 🎉 Let’s start by grabbing two perfect slices of bread—aren’t you excited already?! Spread the peanut butter on one slice—get a nice, even layer! Wow, look at you go! Now for the jelly—smooth it out over the other slice, just the right amount, you’re doing fantastic! Finally, carefully press the two slices together—yes, this is the moment of greatness! You did it! 👏 Now cut it into halves or quarters if you like. Bravo, you’ve made the perfect PB&J!`,
    },
    {
        src: image7,
        sample: `First, take two identical slices of bread and ensure they are properly aligned. Apply one tablespoon of peanut butter evenly across one slice, covering all areas. Do the same with exactly one tablespoon of jelly on the second slice, ensuring no excess. Once both slices are prepared, press them together carefully. Be sure the edges are perfectly aligned. Cut the sandwich in half for optimal presentation. Your peanut butter and jelly sandwich is now complete.`,
    },
    {
        src: image8,
        sample: `Whoohoo! Let’s dive into making this sandwich—it’s going to be awesome! 🎉 Grab any kind of bread that speaks to you, no rules here! Spread that peanut butter, as much or as little as you like—go wild! Now, hit that jelly, again, you do you! Want more? Less? It’s all good! Finally, press the slices together and marvel at what you’ve created. No need to be precise, you’re doing an amazing job! Cut it if you want, or leave it whole. Either way, you’ve totally rocked this!`,
    },
];

export const Instructors = () => {
    const [selectedInstructorIndex, setSelectedInstructorIndex] =
        useState<number>(0);

    return (
        <Container size="xl">
            <Box style={{ border: "1px solid #424242" }} px="xl" py="xl">
                <Stack>
                    <Title order={3} c="#8DCAFF">
                        Your AI Instructor is Always Here for You
                    </Title>

                    <Text c="gray" size="sm">
                        Learning new skills comes with questions—big and small.
                        Don’t hold back. <b>Eduvize’s AI Instructor</b> is your
                        personal guide, ready to answer any question, no matter
                        how complex or simple. It’s like having a mentor right
                        by your side, always helping you move forward with
                        confidence.
                    </Text>

                    <Group justify="center" gap="lg" my="xl">
                        {instructors.map(({ src }, index) => (
                            <InstructorButton
                                src={src}
                                selected={selectedInstructorIndex === index}
                                onSelect={() =>
                                    setSelectedInstructorIndex(index)
                                }
                                key={index}
                            />
                        ))}
                    </Group>

                    <Text c="#8DCAFF" size="sm" fs="italic">
                        How Does This Instructor Make a PB & J?
                    </Text>

                    <Text c="gray" size="sm" fs="italic">
                        “{instructors[selectedInstructorIndex].sample}”
                    </Text>
                </Stack>
            </Box>
        </Container>
    );
};
