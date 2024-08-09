import {
    Box,
    Button,
    Card,
    Container,
    Divider,
    Flex,
    Grid,
    Skeleton,
    Space,
    Stack,
    Text,
    Title,
} from "@mantine/core";
import { memo, useEffect, useRef, useState } from "react";
import { useCurrentUser } from "../../context/user/hooks";
import { useForm, UseFormReturnType } from "@mantine/form";
import {
    BasicInfoStep,
    EducationStep,
    HobbiesStep,
    ProfessionalStep,
    ProficiencyStep,
} from "./steps";
import { ProfileUpdatePayload } from "../../api/contracts/ProfileUpdatePayload";
import { ResumeBanner } from "./ResumeBanner";
import { LearningCapacity } from "../../models/enums";
import { useDebouncedCallback } from "@mantine/hooks";
import { ProfileStepper } from "./ProfileStepper";

export type ProfileStep =
    | "basic"
    | "hobby"
    | "education"
    | "professional"
    | "proficiencies";

function mapCheckListField(
    form: UseFormReturnType<ProfileUpdatePayload>,
    field: string,
    options: any,
    inputProps: any
) {
    const { value } = options;

    function getValueFromDotPath(obj: any, path: string): any {
        return path.split(".").reduce((acc, key) => acc[key], obj);
    }

    return {
        ...inputProps,
        onChange: (checked: boolean) => {
            if (checked) {
                form.setFieldValue(field, [
                    ...getValueFromDotPath(form.values, field),
                    value,
                ]);
            } else {
                form.setFieldValue(
                    field,
                    getValueFromDotPath(form.values, field).filter(
                        (v: any) => v !== value
                    )
                );
            }
        },
        checked: getValueFromDotPath(form.values, field).includes(value),
    };
}

type HeaderInfo = {
    title: string;
    description: string;
};

const HEADERS: Record<ProfileStep, HeaderInfo> = {
    basic: {
        title: "About You",
        description: `
Fill out basic information about yourself so we can get to know you a little bit better. This is high-level information that will be leveraged
in order to match you with the best courses that fit your interests and goals, and allows us to better understand your background and experience.
        `,
    },
    hobby: {
        title: "Hobbies and Interests",
        description: `
We'd like to know a little more about what drives your passion projects. Tell us about what motivates you, what technology you're using, and what projects you've poured your time into.
        `,
    },
    education: {
        title: "Education",
        description: `
Tell us about your academic background, such as where you received formal education, what area of study, and any degrees or certifications you've earned.
        `,
    },
    professional: {
        title: "Professional Experience",
        description: `
Tell us about your professional background and experience, such as where you've worked, what roles you've held, and what technologies you've worked with.
        `,
    },
    proficiencies: {
        title: "Proficiencies",
        description: `
Rate yourself on your listed skills and disciplines. This will help us better understand your comfort levels with different technologies and areas of expertise.
        `,
    },
};

export const Profile = memo(() => {
    const isHydratedRef = useRef(false);
    const initialSetRef = useRef(false);
    const [userDetails, refresh, updateProfile] = useCurrentUser();
    const [canMoveOn, setCanMoveOn] = useState(false);
    const [scanningResume, setScanningResume] = useState(false);
    const [currentStep, setCurrentStep] = useState<ProfileStep>("basic");
    const [pendingSave, setPendingSave] = useState(false);
    const form = useForm<ProfileUpdatePayload>({
        initialValues: {
            first_name: "",
            last_name: "",
            birthdate: null,
            bio: null,
            github_username: null,
            skills: [],
            disciplines: [],
            learning_capacities: [],
            hobby: null,
            student: null,
        },
        enhanceGetInputProps: (payload) => {
            switch (payload.field) {
                case "learning_capacities":
                    return mapCheckListField(
                        payload.form,
                        payload.field,
                        payload.options,
                        payload.inputProps
                    );
                case "hobby.skills":
                    return mapCheckListField(
                        payload.form,
                        payload.field,
                        payload.options,
                        payload.inputProps
                    );
                case "hobby.reasons":
                    return mapCheckListField(
                        payload.form,
                        payload.field,
                        payload.options,
                        payload.inputProps
                    );
            }

            return payload.inputProps;
        },
    });

    useEffect(() => {
        if (!userDetails) {
            return;
        }

        form.setValues({
            ...userDetails.profile,
            birthdate: userDetails.profile.birthdate
                ? new Date(userDetails.profile.birthdate)
                : null,
            learning_capacities:
                userDetails.profile.selected_learning_capacities ||
                userDetails.profile.learning_capacities,
            hobby: userDetails.profile.hobby
                ? {
                      ...userDetails.profile.hobby,
                      skills: userDetails.profile.hobby.skills.map(
                          (skill) =>
                              userDetails.profile.skills.find(
                                  (s) => s.id === skill
                              )!.skill
                      ),
                  }
                : null,
        });

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
    }, [form.values.learning_capacities]);

    const handleAutoUpdate = useDebouncedCallback(() => {
        updateProfile(form.values);
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
                            {HEADERS[currentStep].title}
                        </Title>
                        <Divider my="xs" />
                        <Text size="sm" c="gray">
                            {HEADERS[currentStep].description}
                        </Text>
                    </Stack>
                </Grid.Col>
            </Grid>
        );
    };

    return (
        <Container size="lg">
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
                                        Parsing your resume...
                                    </Text>
                                </Stack>
                            </Box>

                            {currentStep === "basic" && (
                                <BasicInfoStep
                                    userDetails={userDetails}
                                    form={form}
                                    onAvatarChange={() => refresh()}
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
                                <EducationStep form={form} />
                            )}

                            {currentStep === "professional" && (
                                <ProfessionalStep form={form} />
                            )}

                            {currentStep === "proficiencies" && (
                                <ProficiencyStep form={form} />
                            )}

                            <Space h="xl" />

                            {canMoveOn && (
                                <Flex justify="flex-end">
                                    <Button variant="outline">
                                        Let's move on
                                    </Button>
                                </Flex>
                            )}
                        </Card>
                    </Grid.Col>

                    <Grid.Col span={1} pos="relative">
                        <Box pos="absolute" w="15em" ml="xl">
                            <ResumeBanner
                                form={form}
                                onParsing={() => setScanningResume(true)}
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
