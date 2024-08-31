import { Group, Button, Text, Title, Stack } from "@mantine/core";
import { AdditionalInputsDto } from "@models/dto";
import { CoursePlanningFollowUp } from "@organisms";
import { useState } from "react";

interface SecondStepProps {
    followupInformation: AdditionalInputsDto;
    onBack: () => void;
    onContinue: (data: any) => void;
}

export const SecondStep = ({
    followupInformation,
    onBack,
    onContinue,
}: SecondStepProps) => {
    const [answers, setAnswers] = useState<any>({});

    return (
        <>
            <Stack gap={0}>
                <Title order={2}>Additional Information</Title>
                <Text c="dimmed">
                    Please provide additional information to help us better
                    understand your needs.
                </Text>
            </Stack>

            <CoursePlanningFollowUp
                inputs={followupInformation.inputs}
                onChange={(data) => setAnswers(data)}
            />

            <Group justify="flex-end" mt="xl">
                <Group>
                    <Button variant="subtle" onClick={onBack}>
                        Back
                    </Button>

                    <Button
                        variant="gradient"
                        onClick={() => onContinue(answers)}
                    >
                        Continue
                    </Button>
                </Group>
            </Group>
        </>
    );
};
