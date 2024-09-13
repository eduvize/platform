import { PlaygroundProvider } from "@context/playground";
import { Card, Container, Divider, Input, Space, Text } from "@mantine/core";
import { Playground } from "@organisms";
import { useState } from "react";

export const PlaygroundTest = () => {
    const [value, setValue] = useState<string>("");
    const [environmentId, setEnvironmentId] = useState<string | null>("");

    if (!environmentId) {
        return (
            <Container size="sm" pt="xl">
                <Card withBorder>
                    <Text size="xl">Playground Tester</Text>
                    <Divider my="sm" />
                    <Text size="sm">
                        Enter a valid environment ID (found in the database)
                    </Text>

                    <Space h="md" />

                    <Input
                        mx="xl"
                        value={value}
                        onChange={(event) => setValue(event.target.value)}
                        onKeyDown={(event) => {
                            if (event.key === "Enter") {
                                setEnvironmentId(value);
                            }
                        }}
                    />
                </Card>
            </Container>
        );
    }

    return (
        <PlaygroundProvider environmentId={environmentId}>
            <Playground height="600px" />
        </PlaygroundProvider>
    );
};
