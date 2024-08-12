import { useEffect, useRef, useState } from "react";
import { useNavigation } from "react-router-dom";
import { ValidationApi } from "@api";
import { useInstructor } from "@context/user/hooks";
import {
    Button,
    Text,
    Stack,
    InputLabel,
    Input,
    Card,
    Avatar,
    Group,
    Center,
    Divider,
    Loader,
} from "@mantine/core";
import { useDebouncedCallback } from "@mantine/hooks";
import classes from "./InstructorSetup.module.css";

export const InstructorSetup = () => {
    const [instructor, generate, approve] = useInstructor();
    const lastInstructorRef = useRef(instructor?.avatar_url);
    const [animalName, setAnimalName] = useState("");
    const [redo, setRedo] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [isValid, setIsValid] = useState(!!instructor);
    const [isValidating, setIsValidating] = useState(false);
    const [_, setValidationError] = useState<string | null>(null);

    const handleGenerate = () => {
        setIsLoading(true);
        generate(animalName);
    };

    const handleRedo = () => {
        setRedo(true);
    };

    const handleApprove = () => {
        approve().finally(() => {
            window.location.reload();
        });
    };

    const handleValidate = useDebouncedCallback(() => {
        if (!animalName) {
            setIsValid(false);
            setValidationError(null);
            return;
        }

        ValidationApi.assert(
            `${animalName} is a valid animal or creature name, either real or fictional.`
        )
            .then((res) => {
                setIsValid(res.assertion);

                if (!res.assertion) {
                    setValidationError(res.reason);
                } else {
                    setValidationError(null);
                }
            })
            .finally(() => {
                setIsValidating(false);
            });
    }, 500);

    useEffect(() => {
        if (!animalName) {
            return;
        }

        setIsValidating(true);
        setIsValid(false);
        setValidationError(null);

        handleValidate();
    }, [animalName]);

    useEffect(() => {
        if (instructor?.avatar_url === lastInstructorRef.current) {
            return;
        }

        if (instructor) {
            setIsLoading(false);
            setRedo(false);
            setIsValid(true);
        }
    }, [instructor]);

    const TryAgainButton = () => {
        return (
            <Button
                bg="gray"
                size="sm"
                radius="sm"
                onClick={handleRedo}
                disabled={isLoading}
            >
                Try again
            </Button>
        );
    };

    const CreateButton = () => {
        return (
            <Button
                size="sm"
                radius="sm"
                onClick={handleGenerate}
                disabled={!isValid}
            >
                Create
            </Button>
        );
    };

    const ContinueButton = () => {
        return (
            <Button
                size="sm"
                radius="sm"
                onClick={handleApprove}
                disabled={!isValid || isLoading}
            >
                Let's continue
            </Button>
        );
    };

    return (
        <div className={classes.wrapper}>
            <div className={classes.body}>
                <Text fw={500} fz="xl" mb={5}>
                    Create your instructor
                </Text>
                <Text fz="sm" c="dimmed">
                    Now that you've completed your profile, it's time to meet
                    your personal instructor who will guide your through your
                    journey on the Eduvize platform.
                </Text>

                {!isLoading && (
                    <Stack>
                        <Divider mt="sm" />

                        {instructor && !redo && (
                            <Card withBorder>
                                <Center>
                                    <Group gap="xl">
                                        <Avatar
                                            src={instructor.avatar_url}
                                            alt={instructor.name}
                                            radius="50%"
                                            size="xl"
                                        />

                                        <Text fw={500} fz="xl">
                                            Say hello to {instructor.name}!
                                        </Text>
                                    </Group>
                                </Center>
                            </Card>
                        )}

                        {(!instructor || redo) && (
                            <Stack gap={0}>
                                <InputLabel required>
                                    {instructor
                                        ? "Enter a new animal"
                                        : "Now, what's your favorite animal?"}
                                </InputLabel>

                                <Input
                                    value={animalName}
                                    onChange={(e) =>
                                        setAnimalName(e.currentTarget.value)
                                    }
                                    placeholder="This can be an animal or another noteworthy creature"
                                    error={
                                        !isValid && animalName && !isValidating
                                    }
                                />

                                {!isValid && !isValidating && (
                                    <Text c="red" size="sm">
                                        Must be a valid animal or creature
                                    </Text>
                                )}
                            </Stack>
                        )}

                        <div className={classes.controls}>
                            <Group>
                                {instructor && !redo && <TryAgainButton />}
                                {(!instructor || redo) && <CreateButton />}
                                {instructor && !redo && <ContinueButton />}
                            </Group>
                        </div>
                    </Stack>
                )}

                {isLoading && (
                    <Center p="xl">
                        <Loader color="blue" size="xl" type="bars" />
                    </Center>
                )}
            </div>
        </div>
    );
};
