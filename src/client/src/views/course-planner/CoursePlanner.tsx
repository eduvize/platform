import { useEffect, useMemo, useState } from "react";
import { ChatProvider } from "@context/chat";
import {
    Box,
    Button,
    Card,
    Center,
    Container,
    Loader,
    Stack,
    Text,
} from "@mantine/core";
import { AdditionalInputsDto, CoursePlan } from "@models/dto";
import { useForm } from "@mantine/form";
import { mapCheckListField } from "../profile/util";
import { FirstStep, SecondStep } from "./steps";
import { CourseApi } from "@api";
import { IconCircleCheck } from "@tabler/icons-react";
import { useNavigate } from "react-router-dom";

enum Step {
    Overview = 0,
    Followup = 1,
    Generation = 2,
}

const Component = () => {
    const navigate = useNavigate();
    const form = useForm<CoursePlan>({
        initialValues: {
            subject: "",
            motivations: [],
            experience: null,
            materials: [],
            followup_answers: {},
            desired_outcome: "",
        },
        enhanceGetInputProps: (payload) => {
            switch (payload.field) {
                case "motivations":
                case "materials":
                    return mapCheckListField<CoursePlan>(
                        payload.form,
                        payload.field,
                        payload.options,
                        payload.inputProps
                    );
                case "experience":
                    return {
                        ...payload.inputProps,
                        onChange: (e: any) => {
                            payload.form.setFieldValue(
                                "experience",
                                payload.options.value
                            );
                        },
                        checked:
                            payload.form.values.experience ===
                            payload.options.value,
                    };
            }

            return payload.inputProps;
        },
    });
    const [step, setStep] = useState<Step>(Step.Overview);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [isFinished, setIsFinished] = useState<boolean>(false);
    const [followup, setFollowup] = useState<AdditionalInputsDto | null>(null);

    useEffect(() => {
        if (step === 1) {
            setIsLoading(true);

            CourseApi.getAdditionalInputs(form.values)
                .then((inputs) => {
                    setFollowup(inputs);
                })
                .finally(() => {
                    setIsLoading(false);
                });
        }
    }, [step]);

    const loadingDescription = useMemo(() => {
        switch (step) {
            case Step.Followup:
                return "Processing your information...";
            case Step.Generation:
                return "Building a course outline based on your answers...";
            default:
                return "Working on it...";
        }
    }, [step]);

    const handleFollowupAnswers = (answers: any) => {
        form.setFieldValue("followup_answers", answers);

        setIsLoading(true);

        CourseApi.generateCourse({
            ...form.values,
            followup_answers: answers,
        }).finally(() => {
            setIsLoading(false);
            setIsFinished(true);
        });

        setStep(Step.Generation);
    };

    if (isLoading)
        return (
            <Box pos="fixed" left="50%" top="50%" w="200px">
                <Stack align="center" gap={0}>
                    <Loader type="bars" />

                    <Text c="dimmed" mt="sm">
                        {loadingDescription}
                    </Text>
                </Stack>
            </Box>
        );

    if (isFinished) {
        return (
            <Container size="xs" pt="xl" mt="xl">
                <Stack gap="xl">
                    <Card withBorder p="xl">
                        <Stack align="center">
                            <IconCircleCheck
                                color="var(--mantine-color-green-5)"
                                size={96}
                            />

                            <Text ta="center" size="xl">
                                Submission successful
                            </Text>

                            <Text ta="center" size="sm" c="dimmed">
                                We've created a course syllabus based on your
                                answers and are working on generating the
                                content right now. This process can take several
                                minutes to complete.
                            </Text>

                            <Text ta="center" size="sm" c="dimmed">
                                You'll receive an email once it's ready!
                            </Text>
                        </Stack>
                    </Card>

                    <Stack px="20%">
                        <Button
                            variant="gradient"
                            onClick={() => {
                                navigate("/dashboard/courses/active");
                            }}
                        >
                            Back to courses
                        </Button>

                        <Button
                            variant="filled"
                            c="dimmed"
                            bg="dark"
                            onClick={() => {
                                setStep(Step.Overview);
                                setIsFinished(false);
                                form.reset();
                            }}
                        >
                            Create another
                        </Button>
                    </Stack>
                </Stack>
            </Container>
        );
    }

    return (
        <Stack>
            <Box pos="relative" p="xl">
                <Center>
                    <Stack gap="xl">
                        {(step === 0 || (step == 1 && isLoading)) && (
                            <FirstStep
                                form={form}
                                onContinue={() => setStep(Step.Followup)}
                            />
                        )}

                        {step >= 1 && followup && (
                            <SecondStep
                                followupInformation={followup}
                                onBack={() => {
                                    setFollowup(null);
                                    setStep(Step.Overview);
                                }}
                                onContinue={handleFollowupAnswers}
                            />
                        )}
                    </Stack>
                </Center>
            </Box>
        </Stack>
    );
};

export const CoursePlanner = () => (
    <ChatProvider>
        <Component />
    </ChatProvider>
);
