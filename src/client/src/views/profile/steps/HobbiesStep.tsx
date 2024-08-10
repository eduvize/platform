import {
    Accordion,
    Button,
    Chip,
    Divider,
    Group,
    Space,
    Stack,
    Text,
    Textarea,
    UnstyledButton,
} from "@mantine/core";
import { SpacedDivider } from "../../../components/molecules";
import { UseFormReturnType } from "@mantine/form";
import { ProfileUpdatePayload } from "../../../api/contracts";
import { ProfileStep } from "../Profile";
import { HobbyProjectDto, HobbyReason } from "../../../models/dto";
import { LearningCapacity, UserSkillType } from "../../../models/enums";
import { useCallback, useMemo } from "react";
import { IconCirclePlusFilled } from "@tabler/icons-react";
import { ProfileAccordion } from "../../../components/organisms";
import { isHobbyInformationComplete } from "../validation";

interface HobbiesStepProps {
    form: UseFormReturnType<ProfileUpdatePayload>;
    onChangeStep: (step: ProfileStep) => void;
}

interface ReasonChipProps {
    label: string;
    value: HobbyReason;
}

export const HobbiesStep = ({ form, onChangeStep }: HobbiesStepProps) => {
    const projects = form.values.hobby?.projects || [];

    const isComplete = useMemo(
        () => isHobbyInformationComplete(form),
        [form.values]
    );

    const moveNext = useCallback(() => {
        if (!isComplete) return;

        // Determine the next step
        if (
            form.values.learning_capacities.includes(LearningCapacity.Student)
        ) {
            onChangeStep("education");
        } else if (
            form.values.learning_capacities.includes(
                LearningCapacity.Professional
            )
        ) {
            onChangeStep("professional");
        } else {
            onChangeStep("proficiencies");
        }
    }, [isComplete, form.values]);

    const handleViewGeneralInfo = () => {
        onChangeStep("basic");
    };

    const handleRemoveProject = (index: number) => {
        form.setFieldValue(
            "hobby.projects",
            projects.filter((_, i) => i !== index)
        );
    };

    const handleAddProject = () => {
        form.setFieldValue("hobby.projects", [
            ...projects,
            {
                name: "Untitled Project",
                description: "",
            },
        ]);
    };

    const handleProjectChange = (
        index: number,
        value: Partial<HobbyProjectDto>
    ) => {
        form.setFieldValue(
            "hobby.projects",
            projects.map((project, i) =>
                i === index ? { ...project, ...value } : project
            )
        );
    };

    const HobbyProject = (project: HobbyProjectDto & { index: number }) => {
        return (
            <>
                <Textarea
                    required
                    {...form.getInputProps(
                        `hobby.projects.${project.index}.description`
                    )}
                    label="Description"
                    rows={3}
                    placeholder="Describe the project and what you accomplished, what challenges you faced, and what you learned."
                />

                <Textarea
                    {...form.getInputProps(
                        `hobby.projects.${project.index}.purpose`
                    )}
                    label="Purpose"
                    rows={3}
                    placeholder="Why did you want to work on it?"
                />
            </>
        );
    };

    const ReasonChip = ({ label, value }: ReasonChipProps) => {
        return (
            <Chip
                {...form.getInputProps("hobby.reasons", {
                    type: "checkbox",
                    value,
                })}
                color="blue"
                size="sm"
            >
                {label}
            </Chip>
        );
    };

    return (
        <Stack>
            <Stack gap={0}>
                <Divider
                    label={
                        <Text c="blue" size="lg" fw="bold">
                            Why do you work on hobby projects?
                        </Text>
                    }
                    labelPosition="left"
                />

                <Text c="gray" size="sm" mb="lg">
                    Help us get an idea of what motivates you to work on side
                    projects.
                </Text>

                <Group justify="center">
                    <ReasonChip
                        label="To Learn New Technologies"
                        value={HobbyReason.LearnNewTechnology}
                    />
                    <ReasonChip
                        label="It's Entertaining"
                        value={HobbyReason.Entertaining}
                    />
                    <ReasonChip
                        label="Trying to Make Money"
                        value={HobbyReason.MakeMoney}
                    />
                    <ReasonChip
                        label="To Diversify My Skills"
                        value={HobbyReason.DiversifySkills}
                    />
                    <ReasonChip
                        label="I Like a Challenge"
                        value={HobbyReason.Challenging}
                    />
                    <ReasonChip
                        label="It's a Creative Outlet"
                        value={HobbyReason.CreativeOutlet}
                    />
                </Group>
            </Stack>

            <Stack gap={0}>
                <SpacedDivider
                    bold
                    label="Programming Languages"
                    labelPosition="left"
                    labelColor="blue"
                    labelSize="lg"
                    spacePlacement="top"
                    spacing="lg"
                />

                <Text c="gray" size="sm" mb="lg">
                    What languages do you typically use? You can this selection
                    from the{" "}
                    <a href="#" onClick={handleViewGeneralInfo}>
                        general information
                    </a>{" "}
                    screen.
                </Text>

                <Group>
                    {form.values.skills
                        .filter((x) => x.skill_type === 1)
                        .map((language) => (
                            <Chip
                                {...form.getInputProps("hobby.skills", {
                                    type: "checkbox",
                                    value: language.skill,
                                })}
                                c="blue"
                            >
                                {language.skill}
                            </Chip>
                        ))}
                </Group>
            </Stack>

            <Stack gap={0}>
                <SpacedDivider
                    bold
                    label="Libraries / Frameworks"
                    labelPosition="left"
                    labelColor="blue"
                    labelSize="lg"
                    spacePlacement="top"
                    spacing="lg"
                />

                <Text c="gray" size="sm" mb="lg">
                    What about libraries and frameworks? You can this selection
                    from the{" "}
                    <a href="#" onClick={handleViewGeneralInfo}>
                        general information
                    </a>{" "}
                    screen.
                </Text>

                <Group>
                    {form.values.skills
                        .filter((x) => x.skill_type === 2)
                        .map((lib) => (
                            <Chip
                                {...form.getInputProps("hobby.skills", {
                                    type: "checkbox",
                                    value: lib.skill,
                                })}
                                c="blue"
                            >
                                {lib.skill}
                            </Chip>
                        ))}
                </Group>
            </Stack>

            <Stack gap={0}>
                <SpacedDivider
                    bold
                    label="Projects"
                    labelPosition="left"
                    labelColor="blue"
                    labelSize="lg"
                    spacePlacement="top"
                    spacing="lg"
                    icon={
                        <UnstyledButton onClick={handleAddProject}>
                            <IconCirclePlusFilled size={22} color="white" />
                        </UnstyledButton>
                    }
                />

                <Text c="gray" size="sm" mb="lg">
                    You don't need to list all of them, but please share a few
                    of your side projects and why you enjoyed them.
                </Text>

                <Accordion chevronPosition="left">
                    {projects.map((project, index) => (
                        <ProfileAccordion
                            index={index}
                            form={form}
                            title={project.project_name || "Untitled Project"}
                            titleField={`hobby.projects.${index}.project_name`}
                            component={
                                <HobbyProject index={index} {...project} />
                            }
                            onRemove={() => handleRemoveProject(index)}
                        />
                    ))}
                </Accordion>
            </Stack>

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
