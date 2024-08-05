import {
    Button,
    Card,
    Container,
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
            programming_languages: [],
            libraries: [],
        },
    });

    const Header = () => {
        return (
            <>
                <Title size={24} c="blue">
                    Your Profile
                </Title>
                <Text size="sm" c="gray">
                    The information you fill out here will be leveraged by our
                    AI to provide you with the best possible experience. Be
                    thorough and honest to see the best results!
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
                    <Grid.Col span={3}>
                        <Space h="xs" />

                        <ProfileStepper
                            steps={steps}
                            onCanMoveOn={setCanMoveOn}
                        />
                    </Grid.Col>

                    <Grid.Col span={9}>
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
                </Grid>
            </Stack>
        </Container>
    );
});
