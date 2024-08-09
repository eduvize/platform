import { UseFormReturnType } from "@mantine/form";
import { ProfileUpdatePayload } from "../../../api/contracts";
import {
    Center,
    Divider,
    Grid,
    Group,
    Rating,
    Stack,
    Text,
} from "@mantine/core";
import { DisciplineProficiency } from "../../../components/molecules";
import { EngineeringDiscipline } from "../../../models/enums";

interface ProficiencyStepProps {
    form: UseFormReturnType<ProfileUpdatePayload>;
}

export const ProficiencyStep = ({ form }: ProficiencyStepProps) => {
    const frontend = form.values.disciplines.find(
        (x) => x.discipline_type === EngineeringDiscipline.Frontend
    );
    const backend = form.values.disciplines.find(
        (x) => x.discipline_type === EngineeringDiscipline.Backend
    );
    const database = form.values.disciplines.find(
        (x) => x.discipline_type === EngineeringDiscipline.Database
    );
    const devops = form.values.disciplines.find(
        (x) => x.discipline_type === EngineeringDiscipline.DevOps
    );

    const handleDisciplineChange = (
        discipline: EngineeringDiscipline,
        proficiency: number
    ) => {
        form.setFieldValue("disciplines", [
            ...form.values.disciplines.filter(
                (x) => x.discipline_type !== discipline
            ),
            {
                discipline_type: discipline,
                proficiency,
            },
        ]);
    };

    const handleSkillChange = (index: number, value: number) => {
        form.setFieldValue("skills", [
            ...form.values.skills.map((skill, i) =>
                i === index ? { ...skill, proficiency: value } : skill
            ),
        ]);
    };

    return (
        <Stack>
            <Stack>
                <Divider
                    label={
                        <Text fw="bold" size="lg" c="blue">
                            Disciplines
                        </Text>
                    }
                    labelPosition="left"
                />

                {!!frontend && (
                    <DisciplineProficiency
                        title="Frontend"
                        value={frontend.proficiency}
                        onChange={(val) =>
                            handleDisciplineChange(
                                EngineeringDiscipline.Frontend,
                                val
                            )
                        }
                    />
                )}

                {!!backend && (
                    <DisciplineProficiency
                        title="Backend"
                        value={backend.proficiency}
                        onChange={(val) =>
                            handleDisciplineChange(
                                EngineeringDiscipline.Backend,
                                val
                            )
                        }
                    />
                )}

                {!!database && (
                    <DisciplineProficiency
                        title="Database"
                        value={database.proficiency}
                        onChange={(val) =>
                            handleDisciplineChange(
                                EngineeringDiscipline.Database,
                                val
                            )
                        }
                    />
                )}

                {!!devops && (
                    <DisciplineProficiency
                        title="Infrastructure / DevOps"
                        value={devops.proficiency}
                        onChange={(val) =>
                            handleDisciplineChange(
                                EngineeringDiscipline.DevOps,
                                val
                            )
                        }
                    />
                )}
            </Stack>

            <Stack>
                <Divider
                    label={
                        <Text fw="bold" size="lg" c="blue">
                            Technology
                        </Text>
                    }
                    labelPosition="left"
                />

                {form.values.skills.map((skill, index) => (
                    <Grid>
                        <Grid.Col span={6}>
                            <Text size="lg">{skill.skill}</Text>
                        </Grid.Col>

                        <Grid.Col span={6}>
                            <Center>
                                <Rating
                                    defaultValue={2}
                                    color="teal"
                                    size="lg"
                                    count={4}
                                    value={skill.proficiency || 0}
                                    onChange={(val) =>
                                        handleSkillChange(index, val)
                                    }
                                />
                            </Center>
                        </Grid.Col>
                    </Grid>
                ))}
            </Stack>
        </Stack>
    );
};
