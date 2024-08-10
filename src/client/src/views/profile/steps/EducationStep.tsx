import { UseFormReturnType } from "@mantine/form";
import { ProfileUpdatePayload } from "../../../api/contracts";
import { SearchInput, SpacedDivider } from "../../../components/molecules";
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
import { ProfileStep } from "../Profile";
import { IconCirclePlusFilled } from "@tabler/icons-react";
import { ProfileAccordion } from "../../../components/organisms";
import AutocompleteApi from "../../../api/AutocompleteApi";
import { SchoolDto } from "../../../models/dto";
import { isEducationInformationComplete } from "../validation";

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

    const handleSchoolChange = (
        index: number,
        value: { school_name?: string; focus?: string }
    ) => {
        form.setFieldValue(
            "student.schools",
            schools.map((school, i) =>
                i === index ? { ...school, ...value } : school
            )
        );
    };

    const handleRemoveSchool = (index: number) => {
        form.setFieldValue(
            "student.schools",
            schools.filter((_, i) => i !== index)
        );
    };

    const School = (school: SchoolDto & { index: number }) => {
        return (
            <>
                <SearchInput
                    required
                    {...form.getInputProps(
                        `student.schools.${school.index}.focus`
                    )}
                    valueFetch={(query) =>
                        AutocompleteApi.getEducationalFocuses(
                            school.school_name,
                            query
                        )
                    }
                    label="Primary Focus"
                    placeholder="Major, program, or focus area"
                    disabled={!school.school_name}
                />
            </>
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
                        component={<School index={index} {...school} />}
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
