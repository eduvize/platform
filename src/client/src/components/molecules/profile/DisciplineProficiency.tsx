import { Text, Grid, Center, Rating } from "@mantine/core";

interface DisciplineProficiencyProps {
    title: string;
    value?: number | null;
    onChange?: (value: number) => void;
}

export const DisciplineProficiency = ({
    title,
    value,
    onChange,
}: DisciplineProficiencyProps) => {
    const val = value || 0;

    return (
        <Grid>
            <Grid.Col span={6}>
                <Text size="lg">{title}</Text>
            </Grid.Col>

            <Grid.Col span={6}>
                <Center>
                    <Rating
                        defaultValue={3}
                        color="teal"
                        size="lg"
                        count={4}
                        value={val}
                        onChange={(val) => !!val && onChange?.(val)}
                    />
                </Center>
            </Grid.Col>
        </Grid>
    );
};
