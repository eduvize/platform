import { Input, Stack, Text } from "@mantine/core";
import { AdditionalInputDto } from "@models/dto";
import { FollowUpField } from "@molecules";
import { useState } from "react";

interface CoursePlanningFollowUpProps {
    inputs: AdditionalInputDto[];
}

export const CoursePlanningFollowUp = ({
    inputs,
}: CoursePlanningFollowUpProps) => {
    const [data, setData] = useState<Record<string, string | string[]>>(
        Object.fromEntries(
            inputs.map((input) => [
                input.name,
                input.input_type === "multiselect" ? [] : "",
            ])
        )
    );

    const shouldShowInput = (input: AdditionalInputDto) => {
        if (!input.depends_on_input_name) return true;

        const dependsOnField = inputs.find(
            (i) => i.name === input.depends_on_input_name
        );
        const dependsOnValue = data[input.depends_on_input_name];

        if (!dependsOnValue) return false;

        if (dependsOnField?.input_type === "multiselect") {
            return dependsOnValue.includes(
                input.depends_on_input_value as string
            );
        }

        return dependsOnValue === input.depends_on_input_value;
    };

    return (
        <Stack>
            {inputs.filter(shouldShowInput).map((input) => (
                <Input.Wrapper
                    required={input.required}
                    label={input.short_label}
                    mb="sm"
                >
                    {input.description && (
                        <Text c="dimmed" size="sm" mb="sm">
                            {input.description}
                        </Text>
                    )}

                    <FollowUpField
                        {...input}
                        value={data[input.name]}
                        onChange={(value) =>
                            setData({ ...data, [input.name]: value })
                        }
                    />
                </Input.Wrapper>
            ))}
        </Stack>
    );
};
