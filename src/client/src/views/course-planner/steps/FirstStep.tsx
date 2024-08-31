import { useEffect, useMemo, useState } from "react";
import {
    Stack,
    Input,
    Group,
    Chip,
    Textarea,
    Button,
    Text,
    Switch,
} from "@mantine/core";
import { UseFormReturnType } from "@mantine/form";
import { CoursePlan } from "@models/dto";
import {
    CourseMaterial,
    CourseMotivation,
    CurrentSubjectExperience,
} from "@models/enums";

const MOTIVATION_LABELS: Record<string, string> = {
    [CourseMotivation.Career]: "Career Advancement",
    [CourseMotivation.SkillEnhancement]: "Skill Enhancement",
    [CourseMotivation.Project]: "Project Requirement",
    [CourseMotivation.Certification]: "Certification Preparation",
    [CourseMotivation.Other]: "Other",
};

const CURRENT_EXPERIENCE_LABELS: Record<string, string> = {
    [CurrentSubjectExperience.New]: "I'm brand new to this",
    [CurrentSubjectExperience.Refresh]: "I need a refresher",
    [CurrentSubjectExperience.Existing]: "I have some experience",
    [CurrentSubjectExperience.Knowledgeable]: "I already know a lot",
};

const MATERIAL_LABELS: Record<string, string> = {
    [CourseMaterial.Reading]: "Reading Material",
    [CourseMaterial.Practice]: "Hands-on Practice",
    [CourseMaterial.Project]: "Project Work",
};

interface FirstStepProps {
    form: UseFormReturnType<CoursePlan>;
    onContinue: () => void;
}

export const FirstStep = ({ form, onContinue }: FirstStepProps) => {
    const experienceDescription = useMemo(() => {
        switch (form.values.experience) {
            case CurrentSubjectExperience.New:
                return {
                    label: "Starting Point",
                    placeholder:
                        "Describe where you're ideal starting point is...",
                };
            case CurrentSubjectExperience.Existing:
                return {
                    label: "Missing Pieces",
                    placeholder: "Describe where you feel you are lacking...",
                };
            case CurrentSubjectExperience.Knowledgeable:
                return {
                    label: "Focus Areas",
                    placeholder:
                        "Describe where you'd like to focus and where you feel you can improve...",
                };
            case CurrentSubjectExperience.Refresh:
                return {
                    label: "Refresher Details",
                    placeholder: "Describe what you remember...",
                };
            default:
                return null;
        }
    }, [form.values.experience]);
    const [challenges, setChallenges] = useState(false);

    useEffect(() => {
        if (challenges) {
            form.setFieldValue("challenges", "");
        } else {
            form.setFieldValue("challenges", undefined);
        }
    }, [challenges]);

    return (
        <>
            <Input.Wrapper required label="Subject" size="lg">
                <Text size="sm" c="dimmed">
                    What subject would you like to learn?
                </Text>

                <Input mt="sm" {...form.getInputProps("subject")} />
            </Input.Wrapper>

            <Input.Wrapper required label="Motivations" size="lg">
                <Text size="sm" c="dimmed">
                    What motivates you to learn this subject?
                </Text>

                <Group mt="sm">
                    {Object.entries(MOTIVATION_LABELS).map(([name, label]) => (
                        <Chip
                            color="blue"
                            key={name}
                            {...form.getInputProps("motivations", {
                                type: "checkbox",
                                value: name,
                            })}
                        >
                            {label}
                        </Chip>
                    ))}
                </Group>

                {form.values.motivations.includes(CourseMotivation.Other) && (
                    <Input.Wrapper
                        required
                        label="What other motivations do you have?"
                        {...form.getInputProps("other_motivation_details")}
                        mt="sm"
                    >
                        <Textarea mt="sm" />
                    </Input.Wrapper>
                )}
            </Input.Wrapper>

            <Input.Wrapper required label="Challenges" size="lg">
                <Stack>
                    <Group mt="md">
                        <Switch
                            label="I've faced challenges in the past related to this subject"
                            checked={challenges}
                            onChange={() => setChallenges((c) => !c)}
                        />
                    </Group>

                    {challenges && (
                        <Input.Wrapper
                            required
                            label="Describe the challenges you've faced"
                            {...form.getInputProps("challenges")}
                        >
                            <Textarea mt="sm" />
                        </Input.Wrapper>
                    )}
                </Stack>
            </Input.Wrapper>

            <Input.Wrapper required label="Current Experience" size="lg">
                <Text size="sm" c="dimmed">
                    What is your current experience level with this subject?
                </Text>

                <Stack>
                    <Group mt="sm">
                        {Object.entries(CURRENT_EXPERIENCE_LABELS).map(
                            ([name, label]) => (
                                <Chip
                                    color="blue"
                                    key={name}
                                    {...form.getInputProps("experience", {
                                        type: "checkbox",
                                        value: name,
                                    })}
                                >
                                    {label}
                                </Chip>
                            )
                        )}
                    </Group>

                    {experienceDescription && (
                        <Input.Wrapper
                            required
                            label={experienceDescription.label}
                        >
                            <Textarea
                                mt="sm"
                                placeholder={experienceDescription.placeholder}
                            />
                        </Input.Wrapper>
                    )}
                </Stack>
            </Input.Wrapper>

            <Input.Wrapper required label="Learning Style" size="lg">
                <Text size="sm" c="dimmed">
                    What materials would you like this course to include?
                </Text>

                <Group mt="sm">
                    {Object.entries(MATERIAL_LABELS).map(([name, label]) => (
                        <Chip
                            color="blue"
                            key={name}
                            value={name}
                            {...form.getInputProps("materials", {
                                type: "checkbox",
                                value: name,
                            })}
                        >
                            {label}
                        </Chip>
                    ))}
                </Group>
            </Input.Wrapper>

            <Input.Wrapper required label="Desired Outcome" size="lg">
                <Text size="sm" c="dimmed">
                    What do you hope to achieve by the end of this course?
                </Text>

                <Textarea mt="sm" {...form.getInputProps("desired_outcome")} />
            </Input.Wrapper>

            <Group justify="flex-end" mt="xl">
                <Button variant="gradient" onClick={onContinue}>
                    Continue
                </Button>
            </Group>
        </>
    );
};
