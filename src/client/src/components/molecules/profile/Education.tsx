import { Card, Group, UnstyledButton, Text, Title, Stack } from "@mantine/core";
import { EducationDto } from "../../../models/dto";
import { IconX } from "@tabler/icons-react";
import { SearchInput } from "../input";
import AutocompleteApi from "../../../api/AutocompleteApi";

interface EducationProps extends EducationDto {
    title: string;
    onRemove?: () => void;
    onChange?: (value: EducationDto) => void;
}

export const Education = (education: EducationProps) => {
    const { title, institution, focus, onChange, onRemove } = education;

    const handleChange = (value: Partial<EducationDto>) => {
        onChange?.({ ...education, ...value });
    };

    return (
        <Card withBorder>
            <Stack>
                <Group justify="space-between">
                    <Text c="gray" fw="bold" size="md">
                        {title}
                    </Text>

                    <UnstyledButton onClick={onRemove}>
                        <IconX />
                    </UnstyledButton>
                </Group>

                <SearchInput
                    valueFetch={(query) =>
                        AutocompleteApi.getEducationalInstitutions(query)
                    }
                    label="Institution"
                    placeholder="University, college, bootcamp, etc."
                    onChange={(value) => handleChange({ institution: value })}
                />

                <SearchInput
                    valueFetch={(query) =>
                        AutocompleteApi.getEducationalInstitutions(query)
                    }
                    label="Area of Study"
                    placeholder="Major, minor, concentration, etc."
                    onChange={(value) => handleChange({ focus: value })}
                />
            </Stack>
        </Card>
    );
};
