import { Textarea } from "@mantine/core";
import { UseFormReturnType } from "@mantine/form";
import { ProfileUpdatePayload } from "../../../api/contracts";
import { HobbyProjectDto } from "../../../models/dto/profile";

export const HobbyProject = (
    project: HobbyProjectDto & {
        form: UseFormReturnType<ProfileUpdatePayload>;
        index: number;
    }
) => {
    const { form } = project;

    return (
        <>
            <Textarea
                required
                {...form.getInputProps(
                    `hobby.projects.${project.index}.description`
                )}
                label="Description"
                rows={5}
                placeholder="Describe the project and what you accomplished, what challenges you faced, and what you learned."
            />

            <Textarea
                {...form.getInputProps(
                    `hobby.projects.${project.index}.purpose`
                )}
                label="Purpose"
                rows={5}
                placeholder="Why did you want to work on it?"
            />
        </>
    );
};
