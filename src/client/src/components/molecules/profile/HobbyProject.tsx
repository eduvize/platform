import {
    Card,
    Group,
    Text,
    UnstyledButton,
    Space,
    Textarea,
    Stack,
} from "@mantine/core";
import { HobbyProjectDto } from "../../../models/dto";
import { IconX } from "@tabler/icons-react";

interface HobbyProjectProps extends HobbyProjectDto {
    onRemove?: () => void;
    onChange?: (value: HobbyProjectDto) => void;
}

export const HobbyProject = (project: HobbyProjectProps) => {
    const { project_name, description, purpose, onRemove, onChange } = project;

    const handleChange = (value: Partial<HobbyProjectDto>) => {
        onChange?.({ ...project, ...value });
    };

    return (
        <Card withBorder>
            <Stack>
                <Group justify="space-between">
                    <Text
                        c="gray"
                        size="md"
                        fw="bold"
                        contentEditable
                        style={{ outline: "none" }}
                        onBlur={(e) =>
                            handleChange({
                                project_name:
                                    e.currentTarget.textContent ||
                                    "Untitled Project",
                            })
                        }
                    >
                        {project_name || "Untitled Project"}
                    </Text>

                    <UnstyledButton onClick={onRemove}>
                        <IconX />
                    </UnstyledButton>
                </Group>

                <Textarea
                    label="Description"
                    rows={3}
                    placeholder="Describe the project and what you accomplished, what challenges you faced, and what you learned."
                    value={description}
                    onChange={(e) =>
                        handleChange({ description: e.currentTarget.value })
                    }
                />

                <Textarea
                    label="Purpose"
                    rows={3}
                    placeholder="Why did you want to work on it?"
                    value={purpose}
                    onChange={(e) =>
                        handleChange({ purpose: e.currentTarget.value })
                    }
                />
            </Stack>
        </Card>
    );
};
