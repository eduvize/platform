import {
    Title,
    Container,
    Accordion,
    ThemeIcon,
    rem,
    Button,
    Center,
    Space,
    Divider,
} from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";
import classes from "./Faq.module.css";

const items = [
    {
        value: "get-started",
        title: "How do I get started?",
        content: `
Once you create an account, you'll be asked to fill out some information about yourself; this will help us tailor the experience to your needs.
`,
    },
    {
        value: "pricing",
        title: "How much does it cost?",
        content: `
The Eduvize platform as a service is free for your first few courses. After that, you'll need to subscribe to a plan that suits your needs. Don't want to pay us? No problem! The entire platform is open-source and, given your technical know-how, you can host it yourself.
We're committed to making education accessible to everyone - even if it means giving it away for free.
`,
    },
    {
        value: "open-source-why",
        title: "Why is Eduvize open-source?",
        content: `
We believe that learning new things is a fundamental right. By making Eduvize open-source, we're giving you the freedom to learn and grow without restriction. Now of course, there are some technical hurdles to overcome to host it on your own infrastructure, but we're comitted to giving you the pieces to get you started.
By making Eduvize open-source, we're also able to get feedback from the community and improve the platform for everyone.
Of course, we do still value those who choose to subscribe to the platform service - it helps us keep the lights on and continue to improve the platform.        
`,
    },
    {
        value: "open-source-licensing",
        title: "What license is Eduvize under?",
        content: `
We're happy to give the code away for free, but we do have some restrictions on how you can use it - mostly around attribution and not using it for commercial purposes. We're using the Creative Commons Attribution-NonCommercial 4.0 International License, which you can read more about [here](http://creativecommons.org/licenses/by-nc/4.0/).
This means that you can use Eduvize for free, but you must give credit to the original authors and you can't use it to make money without our permission. Want to incorporate it into your own platform? Just ask us - we're happy to learn more!
`,
    },
];

export function Faq() {
    const parseMarkdownUrls = (content: string) => {
        return content.replace(
            /\[(.*?)\]\((.*?)\)/g,
            '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
        );
    };

    return (
        <div className={classes.wrapper}>
            <Container size="md">
                <Title ta="center" className={classes.title}>
                    Frequently Asked Questions
                </Title>

                <Accordion
                    chevronPosition="right"
                    defaultValue="reset-password"
                    chevronSize={26}
                    variant="separated"
                    disableChevronRotation
                    styles={{
                        label: { color: "var(--mantine-color-black)" },
                        item: { border: 0 },
                    }}
                    chevron={
                        <ThemeIcon
                            radius="xl"
                            className={classes.gradient}
                            size={26}
                        >
                            <IconPlus
                                style={{ width: rem(18), height: rem(18) }}
                                stroke={1.5}
                            />
                        </ThemeIcon>
                    }
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
                                        __html: parseMarkdownUrls(itm.content),
                                    }}
                                />
                            </Accordion.Panel>
                        </Accordion.Item>
                    ))}
                </Accordion>

                <Space h="xl" />
                <Space h="xl" />

                <Divider label="What are you waiting for?" />

                <Space h="xl" />

                <Center>
                    <Button size="xl">Start your journey</Button>
                </Center>
            </Container>
        </div>
    );
}
