import { Stack, Group, Switch, InputLabel, Grid } from "@mantine/core";
import { DateInput } from "@mantine/dates";
import { UseFormReturnType } from "@mantine/form";
import AutocompleteApi from "../../../api/AutocompleteApi";
import { ProfileUpdatePayload } from "../../../api/contracts";
import { SchoolDto } from "../../../models/dto/profile";
import { SearchInput } from "../input";

export const School = (
    school: SchoolDto & {
        form: UseFormReturnType<ProfileUpdatePayload>;
        index: number;
    }
) => {
    const { form } = school;

    return (
        <Stack>
            <SearchInput
                required
                {...form.getInputProps(`student.schools.${school.index}.focus`)}
                valueFetch={(query) =>
                    AutocompleteApi.getEducationalFocuses(
                        school.school_name,
                        query
                    )
                }
                label="Primary Focus"
                placeholder="Major, program, or focus area"
                disabled={!school.school_name}
            />

            <Group>
                <Switch
                    {...form.getInputProps(
                        `student.schools.${school.index}.is_current`,
                        { type: "checkbox" }
                    )}
                />

                <InputLabel>I'm currently attending</InputLabel>
            </Group>

            <Grid>
                <Grid.Col span={!school.is_current ? 6 : 12}>
                    <Stack gap={0}>
                        <InputLabel required>Start Date</InputLabel>
                        <DateInput
                            required
                            {...form.getInputProps(
                                `student.schools.${school.index}.start_date`
                            )}
                            placeholder="MM/YYYY"
                            valueFormat="MM/YYYY"
                        />
                    </Stack>
                </Grid.Col>

                <Grid.Col span={!school.is_current ? 6 : 12}>
                    {!school.is_current && (
                        <Stack gap={0}>
                            <InputLabel required>End Date</InputLabel>
                            <DateInput
                                {...form.getInputProps(
                                    `student.schools.${school.index}.end_date`
                                )}
                                placeholder="MM/YYYY"
                                valueFormat="MM/YYYY"
                            />
                        </Stack>
                    )}
                </Grid.Col>
            </Grid>

            {!school.is_current && (
                <Group>
                    <Switch
                        {...form.getInputProps(
                            `student.schools.${school.index}.did_finish`,
                            { type: "checkbox" }
                        )}
                    />

                    <InputLabel>I finished the program</InputLabel>
                </Group>
            )}
        </Stack>
    );
};
