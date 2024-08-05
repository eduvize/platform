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
import { useForm } from "@mantine/form";
import { BasicInfoStep, ProfileStepper } from "./steps";
import { ProfileUpdatePayload } from "../../../../api/contracts/ProfileUpdatePayload";
import { ResumeBanner } from "./ResumeBanner";

export const Profile = memo(() => {
    const [userDetails, refresh] = useCurrentUser();
    const [steps, setSteps] = useState(["basic"]);
    const [canMoveOn, setCanMoveOn] = useState(false);
    const form = useForm<ProfileUpdatePayload>({
        initialValues: {
            first_name: userDetails?.profile?.first_name || "",
            last_name: userDetails?.profile?.last_name || "",
            bio: userDetails?.profile?.bio || "",
            github_username: userDetails?.profile?.github_username || "",
            disciplines: [],
            programming_languages: [],
            libraries: [],
        },
        enhanceGetInputProps: (payload) => {
            switch (payload.field) {
                case "disciplines":
                    const { value } = payload.options;

                    return {
                        ...payload.inputProps,
                        onChange: (checked: boolean) => {
                            if (checked) {
                                payload.form.setFieldValue("disciplines", [
                                    ...payload.form.values.disciplines,
                                    value,
                                ]);
                            } else {
                                payload.form.setFieldValue(
                                    "disciplines",
                                    payload.form.values.disciplines.filter(
                                        (v) => v !== value
                                    )
                                );
                            }
                        },
                        checked:
                            payload.form.values.disciplines.includes(value),
                    };
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

    const handleToggleStep = (step: string) => {
        if (steps.includes(step)) {
            setSteps(steps.filter((s) => s !== step));
        } else {
            setSteps([...steps, step]);
        }
    };

    return (
        <Container size="lg">
            <Stack>
                <Grid>
                    <Grid.Col span={3} pt="xl">
                        <Space h="8em" />

                        <ProfileStepper
                            steps={steps}
                            onCanMoveOn={setCanMoveOn}
                        />
                    </Grid.Col>

                    <Grid.Col span={8}>
                        <Header />

                        <Space h="lg" />

                        <Card shadow="xs" padding="xl" withBorder>
                            <BasicInfoStep
                                userDetails={userDetails}
                                toggleStep={handleToggleStep}
                                form={form}
                                onAvatarChange={() => refresh()}
                            />
                            {/*<HobbiesStep />*/}

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
            </Stack>
        </Container>
    );
});
