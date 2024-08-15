import { ProfileUpdatePayload } from "@contracts";
import { EmploymentDto } from "@models/dto";
import {
    Stack,
    Group,
    Switch,
    InputLabel,
    Grid,
    Input,
    Textarea,
} from "@mantine/core";
import { DateInput } from "@mantine/dates";
import { UseFormReturnType } from "@mantine/form";

export const Employment = (
    employment: EmploymentDto & {
        form: UseFormReturnType<ProfileUpdatePayload>;
        index: number;
    }
) => {
    const { form } = employment;

    return (
        <>
            <Stack gap={0}>
                <Group>
                    <Switch
                        {...form.getInputProps(
                            `professional.employers.${employment.index}.is_current`,
                            { type: "checkbox" }
                        )}
                    />
                    <InputLabel>I'm working here now</InputLabel>
                </Group>
            </Stack>

            <Grid>
                <Grid.Col span={employment.is_current ? 12 : 6}>
                    <InputLabel required>Start Date</InputLabel>
                    <DateInput
                        required
                        {...form.getInputProps(
                            `professional.employers.${employment.index}.start_date`
                        )}
                        placeholder="MM/YYYY"
                        valueFormat="MM/YYYY"
                    />
                </Grid.Col>

                {!employment.is_current && (
                    <Grid.Col span={6}>
                        <InputLabel required>End Date</InputLabel>
                        <DateInput
                            disabled={employment.is_current}
                            {...form.getInputProps(
                                `professional.employers.${employment.index}.end_date`
                            )}
                            placeholder="MM/YYYY"
                            valueFormat="MM/YYYY"
                        />
                    </Grid.Col>
                )}
            </Grid>

            <Stack gap={0}>
                <InputLabel required>Position</InputLabel>
                <Input
                    required
                    {...form.getInputProps(
                        `professional.employers.${employment.index}.position`
                    )}
                    placeholder="Software Engineer, Data Analyst, etc."
                />
            </Stack>

            <Stack gap={0}>
                <InputLabel required>Description</InputLabel>
                <Textarea
                    required
                    {...form.getInputProps(
                        `professional.employers.${employment.index}.description`
                    )}
                    rows={5}
                    placeholder="Describe your role, responsibilities, and accomplishments."
                />
            </Stack>
        </>
    );
};
