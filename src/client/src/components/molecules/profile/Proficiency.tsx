import { ProfileUpdatePayload } from "@contracts";
import { Text, Grid, Rating, Textarea, Flex, Group } from "@mantine/core";
import { UseFormReturnType } from "@mantine/form";

const MAPPING: Record<number, string> = {
    1: "Beginner",
    2: "Intermediate",
    3: "Advanced",
    4: "Expert",
};

const NOTE_MAPPING: Record<number, string> = {
    1: "What have you learned so far?",
    2: "Where do you feel you're lacking?",
    3: "What do you think you're missing? What do you know already?",
    4: "",
};

interface DisciplineProficiencyProps {
    form: UseFormReturnType<ProfileUpdatePayload>;
    field: string;
    title: string;
    valueFetch: () => number | null;
}

export const Proficiency = ({
    form,
    field,
    title,
    valueFetch,
}: DisciplineProficiencyProps) => {
    const val = valueFetch() || 0;

    return (
        <Grid>
            <Grid.Col span={6}>
                <Text size="lg">{title}</Text>
            </Grid.Col>

            <Grid.Col span={6}>
                <Flex justify="flex-end">
                    <Group gap="xl">
                        <Rating
                            {...form.getInputProps(`${field}.proficiency`)}
                            defaultValue={3}
                            color="teal"
                            size="lg"
                            count={4}
                        />

                        <Text w="80px" size="sm" c="gray" ta="right" pt="0.2em">
                            {!val ? "New" : MAPPING[val]}
                        </Text>
                    </Group>
                </Flex>
            </Grid.Col>

            {val < 4 && (
                <Grid.Col span={12}>
                    <Textarea
                        {...form.getInputProps(`${field}.notes`)}
                        placeholder={NOTE_MAPPING[val]}
                        rows={2}
                    />
                </Grid.Col>
            )}
        </Grid>
    );
};
