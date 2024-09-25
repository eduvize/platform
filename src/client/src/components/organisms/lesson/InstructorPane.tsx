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
    Avatar,
    Text,
} from "@mantine/core";
import { IconSquareMinusFilled } from "@tabler/icons-react";
import { Chat } from "../chat";
import { useResizeObserver, useViewportSize } from "@mantine/hooks";
import { useEffect, useState } from "react";
import { useExercise, useExerciseObjectives } from "@context/exercise/hooks";

interface InstructorPaneProps {
    avatar: string;
    view: "exercise" | "lesson";
    onHide: () => void;
}

export const InstructorPane = ({
    avatar,
    view,
    onHide,
}: InstructorPaneProps) => {
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
                    200
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
                                        ({ objective, is_completed }) => (
                                            <Checkbox
                                                label={objective}
                                                checked={is_completed}
                                                mb="sm"
                                            />
                                        )
                                    )}
                                </List>
                            </>
                        </Card>
                    )}
                </Flex>

                <Flex pos="relative" flex="1 1 auto" mt="xl">
                    <Avatar
                        pos="absolute"
                        top="-55px"
                        left="50%"
                        ml="-42px"
                        src={avatar}
                        size="xl"
                        radius="99999"
                        bg="black"
                        p="sm"
                        styles={{
                            root: {
                                zIndex: 9999,
                            },
                        }}
                    />
                    <Card
                        withBorder
                        ref={chatAreaRef}
                        pos="relative"
                        w="100%"
                        pt="xl"
                    >
                        <Chat
                            maxHeight={chatHeight}
                            greetingMessage="Let me know if you have any questions!"
                        />
                    </Card>
                </Flex>
            </Flex>
        </Stack>
    );
};
