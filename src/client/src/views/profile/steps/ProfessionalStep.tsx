import { ProfileStep } from "../constants";
import { isProfessionalInformationComplete } from "../validation";
import { UseFormReturnType } from "@mantine/form";
import { Employment, SpacedDivider } from "../../../components/molecules";
import { ProfileUpdatePayload } from "../../../api/contracts";
import { Accordion, Button, Space, Text, UnstyledButton } from "@mantine/core";
import { useMemo, useCallback } from "react";
import { IconCirclePlusFilled } from "@tabler/icons-react";
import { ProfileAccordion } from "../../../components/organisms";

interface ProfessionalStepProps {
    form: UseFormReturnType<ProfileUpdatePayload>;
    onChangeStep: (step: ProfileStep) => void;
}

export const ProfessionalStep = ({
    form,
    onChangeStep,
}: ProfessionalStepProps) => {
    const employers = form.values.professional?.employers || [];

    const isComplete = useMemo(
        () => isProfessionalInformationComplete(form),
        [form.values]
    );

    const moveNext = useCallback(() => {
        if (!isComplete) return;

        onChangeStep("proficiencies");
    }, [isComplete, form.values]);

    const handleAddEmployer = () => {
        form.setFieldValue("professional.employers", [
            ...employers,
            {
                company_name: "",
                position: "",
                description: "",
                is_current: false,
                skills: [],
            },
        ]);
    };

    const handleRemoveEmployer = (index: number) => {
        const updatedEmployers = employers.filter((_, i) => i !== index);

        form.setFieldValue("professional.employers", updatedEmployers);
    };

    return (
        <>
            <SpacedDivider
                bold
                label="Employers"
                labelSize="lg"
                labelColor="blue"
                labelPosition="left"
                icon={
                    <UnstyledButton onClick={handleAddEmployer}>
                        <IconCirclePlusFilled size={22} color="white" />
                    </UnstyledButton>
                }
            />

            <Text size="sm" c="gray" mb="md">
                Add your current and past employers.
            </Text>

            <Accordion chevronPosition="left">
                {form.values.professional?.employers.map((employer, index) => (
                    <ProfileAccordion
                        index={index}
                        form={form}
                        title={employer.company_name || `Employer ${index + 1}`}
                        titleField={`professional.employers.${index}.company_name`}
                        skillField={`professional.employers.${index}.skills`}
                        validationFunc={() => {
                            if (!form.values.professional) return false;
                            if (!form.values.professional.employers)
                                return false;

                            const employer =
                                form.values.professional.employers[index];
                            if (!employer) return false;

                            return (
                                !!employer.company_name &&
                                !!employer.position &&
                                !!employer.description &&
                                !!employer.start_date &&
                                (employer.is_current || !!employer.end_date) &&
                                employer.skills.length > 0
                            );
                        }}
                        component={
                            <Employment
                                form={form}
                                index={index}
                                {...employer}
                            />
                        }
                        onRemove={() => handleRemoveEmployer(index)}
                    />
                ))}
            </Accordion>

            <Space h="lg" />

            <Button
                variant="gradient"
                disabled={!isComplete}
                onClick={moveNext}
            >
                Continue
            </Button>
        </>
    );
};
