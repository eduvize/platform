import {
    Box,
    Button,
    Card,
    Container,
    Divider,
    Flex,
    Grid,
    Space,
    Stack,
    Text,
    Title,
} from "@mantine/core";
import { memo, useEffect, useState } from "react";
import { useCurrentUser } from "../../context/user/hooks";
import { useForm, UseFormReturnType } from "@mantine/form";
import {
    BasicInfoStep,
    EducationStep,
    HobbiesStep,
    ProfileStepper,
} from "./steps";
import { ProfileUpdatePayload } from "../../api/contracts/ProfileUpdatePayload";
import { ResumeBanner } from "./ResumeBanner";
import { LearningCapacity } from "../../models/enums";

export type ProfileStep =
    | "basic"
    | "hobby"
    | "education"
    | "professional"
    | "programming";

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

export const Profile = memo(() => {
    const [userDetails, refresh] = useCurrentUser();
    const [canMoveOn, setCanMoveOn] = useState(false);
    const [currentStep, setCurrentStep] = useState<ProfileStep>("basic");
    const form = useForm<ProfileUpdatePayload>({
        initialValues: {
            first_name: userDetails?.profile?.first_name || "",
            last_name: userDetails?.profile?.last_name || "",
            bio: userDetails?.profile?.bio || "",
            github_username: userDetails?.profile?.github_username || "",
            skills: [],
            disciplines: [],
            learning_capacities: [],
            hobby: null,
        },
        enhanceGetInputProps: (payload) => {
            switch (payload.field) {
                case "disciplines":
                case "learning_capacities":
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
        if (form.values.learning_capacities.includes(LearningCapacity.Hobby)) {
            if (!form.values.hobby) {
                form.setFieldValue("hobby", {
                    reasons: [],
                    projects: [],
                });
            }
        } else if (form.values.hobby) {
            form.setFieldValue("hobby", null);
        }
    }, [form.values.learning_capacities]);

    console.log(form.values);

    const Header = () => {
        return (
            <>
                <Title size={24} c="blue" fz="h1">
                    All about you
                </Title>
                <Divider my="xs" />
                <Text size="sm" c="gray">
                    Fill out this comprehensive profile to help us design the
                    perfect AI tutor and courses for you. You can give as much
                    detail as you'd like, but keep in mind the better we're able
                    to understand your background and interests, the better we
                    can work with you.
                </Text>
            </>
        );
    };

    return (
        <Container size="lg">
            <Stack>
                <Grid>
                    <Grid.Col span={3} pt="xl">
                        <Space h="8em" />

                        <ProfileStepper
                            form={form}
                            currentStep={currentStep}
                            onChangeStep={(step) => setCurrentStep(step)}
                        />
                    </Grid.Col>

                    <Grid.Col span={8}>
                        <Header />

                        <Space h="lg" />

                        <Card shadow="xs" padding="xl" withBorder>
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
                        <Box pos="absolute" w="15em" ml="xl" top="9em">
                            <ResumeBanner form={form} />
                        </Box>
                    </Grid.Col>
                </Grid>

                <Space h="xl" />
            </Stack>
        </Container>
    );
});
