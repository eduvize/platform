import { memo, useEffect, useRef, useState } from "react";
import { PROFILE_HEADERS, ProfileStep } from "./constants";
import { ResumeBanner } from "./ResumeBanner";
import { ProfileStepper } from "./ProfileStepper";
import { ProfileUpdatePayload } from "@contracts";
import { useCurrentUser } from "@context/user/hooks";
import { LearningCapacity } from "@models/enums";
import {
    Box,
    Card,
    Container,
    Divider,
    Grid,
    Skeleton,
    Space,
    Stack,
    Text,
    Title,
} from "@mantine/core";
import { useDebouncedCallback } from "@mantine/hooks";
import { useForm } from "@mantine/form";
import {
    mapCheckListField,
    mapInboundProfileData,
    mapOutboundProfileData,
} from "./util";
import {
    BasicInfoStep,
    EducationStep,
    HobbiesStep,
    ProfessionalStep,
    ProficiencyStep,
} from "./steps";

export const Profile = memo(() => {
    const isHydratedRef = useRef(false);
    const initialSetRef = useRef(false);
    const [userDetails, refresh, updateProfile] = useCurrentUser();
    const [scanningResume, setScanningResume] = useState(false);
    const [currentStep, setCurrentStep] = useState<ProfileStep>("basic");
    const [pendingSave, setPendingSave] = useState(false);
    const form = useForm<ProfileUpdatePayload>({
        initialValues: {
            first_name: "",
            last_name: "",
            bio: null,
            github_username: null,
            skills: [],
            disciplines: [],
            learning_capacities: [],
            hobby: null,
            student: null,
            professional: null,
        },
        enhanceGetInputProps: (payload) => {
            switch (payload.field) {
                case "hobby.skills":
                case "hobby.reasons":
                    return mapCheckListField(
                        payload.form,
                        payload.field,
                        payload.options,
                        payload.inputProps
                    );
                default:
                    if (
                        (payload.field.startsWith("student.schools") ||
                            payload.field.startsWith(
                                "professional.employers"
                            )) &&
                        payload.field.endsWith(".skills")
                    ) {
                        return mapCheckListField(
                            payload.form,
                            payload.field,
                            payload.options,
                            payload.inputProps
                        );
                    }
            }

            return payload.inputProps;
        },
    });

    useEffect(() => {
        if (!userDetails) {
            return;
        }

        form.setValues(mapInboundProfileData(userDetails.profile));

        isHydratedRef.current = true;
    }, [!!userDetails]);

    useEffect(() => {
        if (form.values.learning_capacities.includes(LearningCapacity.Hobby)) {
            if (!form.values.hobby) {
                form.setFieldValue("hobby", {
                    skills: [],
                    reasons: [],
                    projects: [],
                });
            }
        } else if (form.values.hobby) {
            form.setFieldValue("hobby", null);
        }

        if (
            form.values.learning_capacities.includes(LearningCapacity.Student)
        ) {
            if (!form.values.student) {
                form.setFieldValue("student", {
                    schools: [],
                });
            }
        } else if (form.values.student) {
            form.setFieldValue("student", null);
        }

        if (
            form.values.learning_capacities.includes(
                LearningCapacity.Professional
            )
        ) {
            if (!form.values.professional) {
                form.setFieldValue("professional", {
                    employers: [],
                });
            }
        } else if (form.values.professional) {
            form.setFieldValue("professional", null);
        }
    }, [form.values.learning_capacities]);

    const handleAutoUpdate = useDebouncedCallback(() => {
        updateProfile(mapOutboundProfileData(form));
        setPendingSave(false);
    }, 1000);

    useEffect(() => {
        if (!isHydratedRef.current) {
            return;
        }

        if (!initialSetRef.current) {
            initialSetRef.current = true;
            return;
        }

        setPendingSave(true);
        handleAutoUpdate();
    }, [form.values]);

    const Header = () => {
        return (
            <Grid>
                <Grid.Col span={3}></Grid.Col>

                <Grid.Col span={8}>
                    <Stack gap={0}>
                        <Title size={24} c="blue" fz="h1">
                            {PROFILE_HEADERS[currentStep].title}
                        </Title>
                        <Divider my="xs" />
                        <Text size="sm" c="gray">
                            {PROFILE_HEADERS[currentStep].description}
                        </Text>
                    </Stack>
                </Grid.Col>
            </Grid>
        );
    };

    return (
        <Container size="lg" pt="lg">
            <Stack>
                <Header />

                <Grid>
                    <Grid.Col span={3}>
                        <ProfileStepper
                            disabled={scanningResume}
                            userDetails={userDetails}
                            pendingSave={pendingSave}
                            form={form}
                            currentStep={currentStep}
                            onChangeStep={(step) => setCurrentStep(step)}
                        />
                    </Grid.Col>

                    <Grid.Col span={8}>
                        <Card shadow="xs" padding="xl" withBorder>
                            <Box
                                display={scanningResume ? "block" : "none"}
                                pos="absolute"
                                left="0"
                                top="0"
                                h="100%"
                                w="100%"
                                style={{ zIndex: 1 }}
                            >
                                <Skeleton
                                    pos="absolute"
                                    w="100%"
                                    h="100%"
                                ></Skeleton>

                                <Stack justify="center" h="100%">
                                    <Text
                                        pos="absolute"
                                        size="xl"
                                        fw="bold"
                                        c="white"
                                        ta="center"
                                        w="100%"
                                        style={{ zIndex: 2 }}
                                    >
                                        Looking over your resume...
                                        <Text size="sm">
                                            This should only take a few seconds,
                                            so hang tight!
                                        </Text>
                                    </Text>
                                </Stack>
                            </Box>

                            {currentStep === "basic" && (
                                <BasicInfoStep
                                    userDetails={userDetails}
                                    form={form}
                                    onAvatarChange={() => refresh()}
                                    onChangeStep={(step) =>
                                        setCurrentStep(step)
                                    }
                                />
                            )}

                            {currentStep === "hobby" && (
                                <HobbiesStep
                                    form={form}
                                    onChangeStep={(step) =>
                                        setCurrentStep(step)
                                    }
                                />
                            )}

                            {currentStep === "education" && (
                                <EducationStep
                                    form={form}
                                    onChangeStep={(step) =>
                                        setCurrentStep(step)
                                    }
                                />
                            )}

                            {currentStep === "professional" && (
                                <ProfessionalStep
                                    form={form}
                                    onChangeStep={(step) =>
                                        setCurrentStep(step)
                                    }
                                />
                            )}

                            {currentStep === "proficiencies" && (
                                <ProficiencyStep form={form} />
                            )}

                            <Space h="xl" />
                        </Card>
                    </Grid.Col>

                    <Grid.Col span={1} pos="relative">
                        <Box pos="absolute" w="15em" ml="xl">
                            <ResumeBanner
                                form={form}
                                onParsing={() => {
                                    setScanningResume(true);
                                    setCurrentStep("basic");
                                }}
                                onScanned={() => {
                                    initialSetRef.current = true;
                                    isHydratedRef.current = true;
                                }}
                                onCompleted={() => setScanningResume(false)}
                            />
                        </Box>
                    </Grid.Col>
                </Grid>

                <Space h="xl" />
            </Stack>
        </Container>
    );
});
