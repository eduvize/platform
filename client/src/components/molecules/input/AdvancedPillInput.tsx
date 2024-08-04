import { PillsInput, Group, UnstyledButton, Pill } from "@mantine/core";

interface AdvancedPillInputProps {
    values: string[];
    onChange: (values: string[]) => void;
}

export const AdvancedPillInput = ({
    values,
    onChange,
}: AdvancedPillInputProps) => {
    const handleValueRemove = (val: string) =>
        onChange(values.filter((v) => v !== val));

    return (
        <PillsInput>
            <Group gap={4}>
                {values.map((lang) => (
                    <UnstyledButton onClick={() => handleValueRemove(lang)}>
                        <Pill
                            key={lang}
                            size="lg"
                            withRemoveButton
                            onRemove={() => {
                                handleValueRemove(lang);
                            }}
                        >
                            {lang}
                        </Pill>
                    </UnstyledButton>
                ))}

                <PillsInput.Field
                    placeholder="Enter a language"
                    onKeyDown={(event) => {
                        if (event.key === "Enter") {
                            onChange([...values, event.currentTarget.value]);
                            event.currentTarget.value = "";
                        }
                    }}
                />
            </Group>
        </PillsInput>
    );
};
