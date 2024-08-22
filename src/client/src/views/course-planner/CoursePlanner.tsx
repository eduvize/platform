import { useEffect, useMemo, useState } from "react";
import { ChatProvider } from "@context/chat";
import {
    Box,
    Card,
    Center,
    Container,
    Loader,
    LoadingOverlay,
    Stack,
    Text,
} from "@mantine/core";
import { AdditionalInputsDto, CoursePlan } from "@models/dto";
import { useForm } from "@mantine/form";
import { mapCheckListField } from "../profile/util";
import { FirstStep, SecondStep } from "./steps";
import { CourseApi } from "@api";

enum Step {
    Overview = 0,
    Followup = 1,
    Generation = 2,
}

const Component = () => {
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
                return "Reviewing your request...";
            case Step.Generation:
                return "Generating your course content...";
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
        });

        setStep(Step.Generation);
    };

    return (
        <Container size="md" p="lg">
            <Stack>
                <Box pos="relative">
                    <LoadingOverlay
                        visible={isLoading}
                        overlayProps={{
                            radius: "md",
                            blur: 1,
                            backgroundOpacity: 1,
                        }}
                        loaderProps={{
                            children: (
                                <Stack>
                                    <Center>
                                        <Loader type="bars" size="lg" />
                                    </Center>

                                    <Text mt="lg">{loadingDescription}</Text>
                                </Stack>
                            ),
                        }}
                    />

                    <Card withBorder p="lg">
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
                    </Card>
                </Box>
            </Stack>
        </Container>
    );
};

export const CoursePlanner = () => (
    <ChatProvider>
        <Component />
    </ChatProvider>
);
