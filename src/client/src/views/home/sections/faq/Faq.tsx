import {
    Title,
    Container,
    Accordion,
    Button,
    Center,
    Space,
    Divider,
    Text,
} from "@mantine/core";
import classes from "./Faq.module.css";
import { Link } from "react-router-dom";

const items = [
    {
        value: "get-started",
        title: "How do I get started?",
        content: `Creating an account is your first step toward personalized learning. Once you've signed up, we'll ask you to provide some details about your background, goals, and areas of interest. This information allows us to tailor the entire experience to meet your unique needs, ensuring that you get the most relevant and effective learning path right from the start. 
        
        Whether you're a beginner or looking to refine specific skills, we'll guide you on your journey to success.
        `,
    },
    {
        value: "pricing",
        title: "How much does it cost?",
        content: `Eduvize offers a generous free tier that allows you to access your first few courses at no cost. After that, you can choose from a variety of subscription plans tailored to fit your needs. 
        
        Not interested in subscribing? That's okay! Our entire platform is open-source, so if you have the technical skills, you're welcome to host it yourself. We're dedicated to making education accessible to everyone—even if that means providing it for free.
`,
    },
    {
        value: "open-source-why",
        title: "Why is Eduvize open-source?",
        content: `We believe that the opportunity to learn and grow should be available to everyone, without barriers. By making Eduvize open-source, we empower you with the freedom to explore, modify, and use the platform on your own terms. While there may be some technical challenges in setting it up on your own infrastructure, we're committed to providing you with the tools and guidance to get started.

Being open-source also means we can harness the power of community feedback to continuously improve the platform for everyone. We genuinely appreciate those who choose to subscribe to our hosted service—your support helps us maintain and enhance Eduvize, ensuring it remains a valuable resource for all.
`,
    },
    {
        value: "open-source-licensing",
        title: "What license is Eduvize under?",
        content: `We're excited to offer Eduvize's code for free, but we do have a few restrictions to ensure it's used responsibly. Eduvize is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License, which you can learn more about [here](http://creativecommons.org/licenses/by-nc/4.0/).

        This license allows you to use Eduvize for free, provided you credit the original authors and refrain from using it for commercial purposes without our permission. 

If you're interested in incorporating Eduvize into your own platform or have other commercial intentions, just reach out to us—we're open to exploring possibilities!
`,
    },
];

export function Faq() {
    const parseMarkdown = (content: string) => {
        return content
            .replace(/\n/g, "<br />")
            .replace(
                /\[(.*?)\]\((.*?)\)/g,
                '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
            );
    };

    return (
        <div className={classes.wrapper}>
            <Container size="sm">
                <Title ta="center" className={classes.title} mb="xl">
                    Frequently Asked Questions
                </Title>

                <Accordion
                    chevronPosition="right"
                    chevronSize={26}
                    variant="separated"
                    styles={{
                        label: { color: "var(--mantine-color-black)" },
                        item: { border: 0 },
                        chevron: { color: "var(--mantine-color-black)" },
                    }}
                >
                    {items.map((itm) => (
                        <Accordion.Item
                            className={classes.item}
                            value={itm.value}
                        >
                            <Accordion.Control className={classes.item_title}>
                                {itm.title}
                            </Accordion.Control>
                            <Accordion.Panel>
                                <div
                                    dangerouslySetInnerHTML={{
                                        __html: parseMarkdown(itm.content),
                                    }}
                                />
                            </Accordion.Panel>
                        </Accordion.Item>
                    ))}
                </Accordion>

                <Space h="xl" />
                <Space h="xl" />

                <Divider
                    label={<Text size="lg">What are you waiting for?</Text>}
                    size="md"
                />

                <Space h="xl" />

                <Center>
                    <Link to="/auth">
                        <Button size="xl">Start for free</Button>
                    </Link>
                </Center>
            </Container>

            <Space h="10em" />
        </div>
    );
}
