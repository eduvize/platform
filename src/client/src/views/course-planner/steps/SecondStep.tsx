import { Group, Button, Text, Title, Stack } from "@mantine/core";
import { AdditionalInputsDto } from "@models/dto";
import { CoursePlanningFollowUp } from "@organisms";

interface SecondStepProps {
    followupInformation: AdditionalInputsDto;
    onBack: () => void;
    onContinue: () => void;
}

export const SecondStep = ({
    followupInformation,
    onBack,
    onContinue,
}: SecondStepProps) => {
    return (
        <>
            <Stack gap={0}>
                <Title order={2}>Additional Information</Title>
                <Text c="dimmed">
                    Please provide additional information to help us better
                    understand your needs.
                </Text>
            </Stack>

            <CoursePlanningFollowUp inputs={followupInformation.inputs} />

            <Group justify="flex-end" mt="xl">
                <Group>
                    <Button variant="subtle" onClick={onBack}>
                        Back
                    </Button>

                    <Button variant="gradient" onClick={onContinue}>
                        Continue
                    </Button>
                </Group>
            </Group>
        </>
    );
};
