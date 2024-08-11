import { ProfileStep } from "../constants";
import { isEducationInformationComplete } from "../validation";
import { UseFormReturnType } from "@mantine/form";
import { ProfileUpdatePayload } from "../../../api/contracts";
import { School, SpacedDivider } from "../../../components/molecules";
import {
    Accordion,
    Button,
    Space,
    Stack,
    Text,
    UnstyledButton,
} from "@mantine/core";
import { useMemo, useCallback } from "react";
import { LearningCapacity } from "../../../models/enums";
import { IconCirclePlusFilled } from "@tabler/icons-react";
import { ProfileAccordion } from "../../../components/organisms";

interface EducationStepProps {
    form: UseFormReturnType<ProfileUpdatePayload>;
    onChangeStep: (step: ProfileStep) => void;
}

export const EducationStep = ({ form, onChangeStep }: EducationStepProps) => {
    const schools = form.values.student?.schools || [];

    const isComplete = useMemo(
        () => isEducationInformationComplete(form),
        [form.values]
    );

    const moveNext = useCallback(() => {
        if (!isComplete) return;

        // Determine the next step
        if (
            form.values.learning_capacities.includes(
                LearningCapacity.Professional
            )
        ) {
            onChangeStep("professional");
        } else {
            onChangeStep("proficiencies");
        }
    }, [isComplete, form.values]);

    const handleAddSchool = () => {
        form.setFieldValue("student.schools", [
            ...schools,
            {
                school_name: "",
                focus: "",
                skills: [],
            },
        ]);
    };

    const handleRemoveSchool = (index: number) => {
        form.setFieldValue(
            "student.schools",
            schools.filter((_, i) => i !== index)
        );
    };

    return (
        <Stack gap={0}>
            <SpacedDivider
                bold
                label="Schools / Institutions"
                labelSize="lg"
                labelColor="blue"
                labelPosition="left"
                icon={
                    <UnstyledButton onClick={handleAddSchool}>
                        <IconCirclePlusFilled size={22} color="white" />
                    </UnstyledButton>
                }
            />

            <Text c="gray" size="sm" mb="md">
                What schools, colleges, bootcamps, or other institutions have
                you attended?
            </Text>

            <Accordion chevronPosition="left">
                {schools.map((school, index) => (
                    <ProfileAccordion
                        index={index}
                        form={form}
                        title={school.school_name || `School #${index + 1}`}
                        titleField={`student.schools.${index}.school_name`}
                        skillField={`student.schools.${index}.skills`}
                        validationFunc={() => {
                            if (!form.values.student) return false;
                            if (!form.values.student.schools) return false;

                            const school = form.values.student.schools[index];
                            if (!school) return false;

                            return (
                                !!school.school_name &&
                                !!school.focus &&
                                !!school.start_date &&
                                (school.is_current || !!school.end_date) &&
                                school.skills.length > 0
                            );
                        }}
                        component={
                            <School form={form} index={index} {...school} />
                        }
                        onRemove={() => handleRemoveSchool(index)}
                    />
                ))}
            </Accordion>

            <SpacedDivider
                bold
                label="Certifications"
                labelPosition="left"
                labelColor="blue"
                labelSize="lg"
                spacePlacement="top"
                spacing="lg"
            />

            <Text c="gray" size="sm" mb="md">
                Do you have any certifications or licenses?
            </Text>

            <Space h="lg" />

            <Button
                variant="gradient"
                disabled={!isComplete}
                onClick={moveNext}
            >
                Continue
            </Button>
        </Stack>
    );
};
