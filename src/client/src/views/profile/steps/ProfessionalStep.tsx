import { UseFormReturnType } from "@mantine/form";
import { SpacedDivider } from "../../../components/molecules";
import { ProfileUpdatePayload } from "../../../api/contracts";
import { Button, Divider, Text } from "@mantine/core";

interface ProfessionalStepProps {
    form: UseFormReturnType<ProfileUpdatePayload>;
}

export const ProfessionalStep = ({ form }: ProfessionalStepProps) => {
    return (
        <>
            <Divider
                label={
                    <Text size="lg" c="blue" fw="bold">
                        Employers
                    </Text>
                }
                labelPosition="left"
            />

            <Text size="sm" c="gray">
                Add your current and past employers.
            </Text>

            <Button
                bg="dark"
                onClick={() => form.setFieldValue("employers", [])}
            >
                Add Employer
            </Button>
        </>
    );
};
