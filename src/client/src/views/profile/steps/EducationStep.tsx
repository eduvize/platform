import { UseFormReturnType } from "@mantine/form";
import { ProfileUpdatePayload } from "../../../api/contracts";
import { Education, SpacedDivider } from "../../../components/molecules";
import { Button, Divider, Stack, Text } from "@mantine/core";

interface EducationStepProps {
    form: UseFormReturnType<ProfileUpdatePayload>;
}

export const EducationStep = ({ form }: EducationStepProps) => {
    const schools = form.values.student?.schools || [];

    const handleAddSchool = () => {
        form.setFieldValue("student.schools", [
            ...schools,
            {
                institution: "",
                focus: "",
            },
        ]);
    };

    const handleSchoolChange = (
        index: number,
        value: { institution?: string; focus?: string }
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

    return (
        <Stack gap={0}>
            <Divider
                label={
                    <Text c="blue" size="lg" fw="bold">
                        Schools / Institutions
                    </Text>
                }
                labelPosition="left"
            />

            <Text c="gray" size="sm" mb="md">
                What schools, colleges, bootcamps, or other institutions have
                you attended?
            </Text>

            <Stack>
                {schools.map((school, index) => (
                    <Education
                        {...school}
                        title={`School #${index + 1}`}
                        onChange={(value) => handleSchoolChange(index, value)}
                        onRemove={() => handleRemoveSchool(index)}
                    />
                ))}

                <Button bg="dark" onClick={handleAddSchool}>
                    {schools.length === 0 ? "Add School" : "Add Another School"}
                </Button>
            </Stack>

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
        </Stack>
    );
};
