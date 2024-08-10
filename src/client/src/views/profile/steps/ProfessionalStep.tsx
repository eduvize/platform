import { UseFormReturnType } from "@mantine/form";
import { SpacedDivider } from "../../../components/molecules";
import { ProfileUpdatePayload } from "../../../api/contracts";
import {
    Accordion,
    Button,
    Group,
    Input,
    InputLabel,
    Space,
    Stack,
    Switch,
    Text,
    Textarea,
    UnstyledButton,
} from "@mantine/core";
import { useMemo, useCallback } from "react";
import { ProfileStep } from "../Profile";
import { IconCirclePlusFilled } from "@tabler/icons-react";
import { ProfileAccordion } from "../../../components/organisms";
import { EmploymentDto } from "../../../models/dto/Employment";
import { isProfessionalInformationComplete } from "../validation";

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

    const Employment = (employment: EmploymentDto & { index: number }) => {
        return (
            <>
                <Stack gap={0}>
                    <Group>
                        <Switch
                            {...form.getInputProps(
                                `professional.employers.${employment.index}.is_current`,
                                { type: "checkbox" }
                            )}
                        />
                        <InputLabel>I'm working here now</InputLabel>
                    </Group>
                </Stack>

                <Stack gap={0}>
                    <InputLabel>Position</InputLabel>
                    <Input
                        required
                        {...form.getInputProps(
                            `professional.employers.${employment.index}.position`
                        )}
                        placeholder="Software Engineer, Data Analyst, etc."
                    />
                </Stack>

                <Stack gap={0}>
                    <InputLabel>Description</InputLabel>
                    <Textarea
                        required
                        {...form.getInputProps(
                            `professional.employers.${employment.index}.description`
                        )}
                        rows={3}
                        placeholder="Describe your role, responsibilities, and accomplishments."
                    />
                </Stack>
            </>
        );
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
                        component={<Employment index={index} {...employer} />}
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
