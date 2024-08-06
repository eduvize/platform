import { Button, Chip, Divider, Grid, Group, Text } from "@mantine/core";
import { HobbyProject, SpacedDivider } from "../../../components/molecules";
import { UseFormReturnType } from "@mantine/form";
import { ProfileUpdatePayload } from "../../../api/contracts";
import { ProfileStep } from "../Profile";
import { HobbyProjectDto } from "../../../models/dto";

interface HobbiesStepProps {
    form: UseFormReturnType<ProfileUpdatePayload>;
    onChangeStep: (step: ProfileStep) => void;
}

export const HobbiesStep = ({ form, onChangeStep }: HobbiesStepProps) => {
    const projects = form.values.hobby?.projects || [];

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

    return (
        <>
            <Divider
                label={
                    <Text c="blue" size="lg" fw="bold">
                        Why do you work on hobby projects?
                    </Text>
                }
                labelPosition="left"
            />

            <Text c="gray" size="sm" mb="lg">
                Select all that apply
            </Text>

            <Group justify="center">
                <Chip>To Learn New Technologies</Chip>
                <Chip>It's Entertaining</Chip>
                <Chip>Trying to Make Money</Chip>
                <Chip>To Diversify My Skills</Chip>
                <Chip>I Like a Challenge</Chip>
                <Chip>It's a Creative Outlet</Chip>
            </Group>

            <SpacedDivider
                bold
                label="Languages"
                labelPosition="left"
                labelColor="blue"
                labelSize="lg"
                spacePlacement="top"
                spacing="lg"
            />

            <Text c="gray" size="sm" mb="lg">
                What languages do you typically use? You can this selection from
                the{" "}
                <a href="#" onClick={handleViewGeneralInfo}>
                    general information
                </a>{" "}
                screen.
            </Text>

            <Group>
                {form.values.skills
                    .filter((x) => x.skill_type === 1)
                    .map((language) => (
                        <Chip c="blue">{language.skill}</Chip>
                    ))}
            </Group>

            <SpacedDivider
                bold
                label="Libraries & Frameworks"
                labelPosition="left"
                labelColor="blue"
                labelSize="lg"
                spacePlacement="top"
                spacing="lg"
            />

            <Text c="gray" size="sm" mb="lg">
                What about libraries and frameworks? You can this selection from
                the{" "}
                <a href="#" onClick={handleViewGeneralInfo}>
                    general information
                </a>{" "}
                screen.
            </Text>

            <Group>
                {form.values.skills
                    .filter((x) => x.skill_type === 2)
                    .map((lib) => (
                        <Chip c="blue">{lib.skill}</Chip>
                    ))}
            </Group>

            <SpacedDivider
                bold
                label="Which projects have been your favorite?"
                labelPosition="left"
                labelColor="blue"
                labelSize="lg"
                spacePlacement="top"
                spacing="lg"
            />

            <Text c="gray" size="sm" mb="lg">
                You don't need to list all of them, but please share a few of
                your side projects and why you enjoyed them.
            </Text>

            <Grid>
                {projects.map((project, index) => (
                    <Grid.Col span={12}>
                        <HobbyProject
                            {...project}
                            onChange={(value) =>
                                handleProjectChange(index, value)
                            }
                            onRemove={() => handleRemoveProject(index)}
                        />
                    </Grid.Col>
                ))}

                <Grid.Col span={12}>
                    <Button color="gray" fullWidth onClick={handleAddProject}>
                        {projects.length === 0
                            ? "Add a Project"
                            : "Add Another"}
                    </Button>
                </Grid.Col>
            </Grid>
        </>
    );
};
