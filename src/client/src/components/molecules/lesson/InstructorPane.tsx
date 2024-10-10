import {
    Stack,
    Flex,
    Group,
    Button,
    Divider,
    Card,
    Space,
    List,
    Checkbox,
    Text,
} from "@mantine/core";
import { IconSquareMinusFilled } from "@tabler/icons-react";
import { Chat } from "../../organisms/chat";
import { useResizeObserver, useViewportSize } from "@mantine/hooks";
import { useEffect, useState } from "react";
import { useExercise, useExerciseObjectives } from "@context/exercise/hooks";

interface InstructorPaneProps {
    view: "exercise" | "lesson";
    onHide: () => void;
}

export const InstructorPane = ({ view, onHide }: InstructorPaneProps) => {
    const exercise = useExercise();
    const objectives = useExerciseObjectives();
    const [chatAreaRef, chatAreaRect] = useResizeObserver();
    const [instructorPaneRef, instructorPaneRect] = useResizeObserver();
    const { height: viewportHeight } = useViewportSize();
    const [chatHeight, setChatHeight] = useState<number>(500);

    useEffect(() => {
        if (chatAreaRect) {
            setChatHeight(
                viewportHeight -
                    chatAreaRect.top -
                    instructorPaneRect.height -
                    240
            );
        }
    }, [chatAreaRect, viewportHeight, instructorPaneRect]);

    return (
        <Stack
            justify="space-between"
            pos="absolute"
            h="calc(100% - 100px)"
            w="23.5%"
        >
            <Flex direction="column" flex="1 0 auto">
                <Flex direction="column" ref={instructorPaneRef}>
                    <Group justify="space-between">
                        <Text tt="uppercase" size="10px">
                            Instructor
                        </Text>

                        <Button p={0} variant="transparent" onClick={onHide}>
                            <IconSquareMinusFilled color="#1479B2" />
                        </Button>
                    </Group>
                    <Divider mb="xl" />
                    <Space h="xl" />

                    {exercise && view === "exercise" && (
                        <Card withBorder mb="xl">
                            <Text size="lg">Exercise Task List</Text>
                            <Text size="xs" c="dimmed">
                                Complete the following objectives to finish this
                                exercise. If you need assistant, ask your
                                instructor.
                            </Text>

                            <>
                                <Space h="xl" />

                                <List listStyleType="none">
                                    {objectives.map(
                                        ({
                                            objective,
                                            description,
                                            is_completed,
                                        }) => (
                                            <Stack gap={0}>
                                                <Checkbox
                                                    label={objective}
                                                    checked={is_completed}
                                                />

                                                <Text
                                                    size="xs"
                                                    c="dimmed"
                                                    mb="sm"
                                                    pl="xl"
                                                >
                                                    {description}
                                                </Text>
                                            </Stack>
                                        )
                                    )}
                                </List>
                            </>
                        </Card>
                    )}
                </Flex>

                <Chat
                    ref={chatAreaRef}
                    maxHeight={chatHeight}
                    greetingMessage="Let me know if you have any questions!"
                />
            </Flex>
        </Stack>
    );
};
