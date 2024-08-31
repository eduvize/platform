import { Textarea, Group, Chip } from "@mantine/core";
import { AdditionalInputDto } from "@models/dto";

interface FollowUpFieldProps extends AdditionalInputDto {
    value: string | string[];
    onChange: (value: string | string[]) => void;
}

export const FollowUpField = ({
    input_type,
    options,
    value,
    onChange,
}: FollowUpFieldProps) => {
    switch (input_type) {
        case "text":
            return (
                <Textarea
                    value={value as string}
                    onChange={(event) => onChange(event.currentTarget.value)}
                />
            );

        case "select":
            const selectValue = value as string;
            return (
                <Group>
                    {(options || []).map((option) => (
                        <Chip
                            c="blue"
                            key={option}
                            checked={option === selectValue}
                            onChange={(checked) => {
                                if (checked) {
                                    onChange(option);
                                }
                            }}
                        >
                            {option}
                        </Chip>
                    ))}
                </Group>
            );

        case "multiselect":
            const arrayValue = value as string[];

            return (
                <Group>
                    {(options || []).map((option) => (
                        <Chip
                            c="blue"
                            key={option}
                            checked={arrayValue.includes(option)}
                            onChange={(checked) => {
                                if (checked) {
                                    onChange([...arrayValue, option]);
                                } else {
                                    onChange(
                                        arrayValue.filter(
                                            (value) => value !== option
                                        )
                                    );
                                }
                            }}
                        >
                            {option}
                        </Chip>
                    ))}
                </Group>
            );
    }
};
