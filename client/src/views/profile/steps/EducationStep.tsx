import { UseFormReturnType } from "@mantine/form";
import { ProfileUpdatePayload } from "../../../api/contracts";
import { SpacedDivider } from "../../../components/molecules";

interface EducationStepProps {
    form: UseFormReturnType<ProfileUpdatePayload>;
}

export const EducationStep = ({ form }: EducationStepProps) => {
    return (
        <SpacedDivider
            bold
            label="Where did you study?"
            labelPosition="left"
            labelColor="blue"
            labelSize="lg"
            spacePlacement="bottom"
            spacing="lg"
        />
    );
};
