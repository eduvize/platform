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
import { memo, useState } from "react";
import { useCurrentUser } from "../../../../context/user/hooks";
import { useForm, UseFormReturnType } from "@mantine/form";
import { BasicInfoStep, HobbiesStep, ProfileStepper } from "./steps";
import { ProfileUpdatePayload } from "../../../../api/contracts/ProfileUpdatePayload";
import { ResumeBanner } from "./ResumeBanner";

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

    return {
        ...inputProps,
        onChange: (checked: boolean) => {
            if (checked) {
                form.setFieldValue(field, [
                    ...(form.values as any)[field],
                    value,
                ]);
            } else {
                form.setFieldValue(
                    field,
                    (form.values as any)[field].filter((v: any) => v !== value)
                );
            }
        },
        checked: (form.values as any)[field].includes(value),
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
            }

            return payload.inputProps;
        },
    });

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
