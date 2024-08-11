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
import { Proficiency } from "../../../components/molecules";
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

    const frontendIndex = form.values.disciplines.findIndex(
        (x) => x.discipline_type === EngineeringDiscipline.Frontend
    );

    const backendIndex = form.values.disciplines.findIndex(
        (x) => x.discipline_type === EngineeringDiscipline.Backend
    );

    const databaseIndex = form.values.disciplines.findIndex(
        (x) => x.discipline_type === EngineeringDiscipline.Database
    );

    const devopsIndex = form.values.disciplines.findIndex(
        (x) => x.discipline_type === EngineeringDiscipline.DevOps
    );

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
                    <Proficiency
                        title="Frontend"
                        form={form}
                        field={`disciplines.${frontendIndex}`}
                        valueFetch={() => frontend.proficiency}
                    />
                )}

                {!!backend && (
                    <Proficiency
                        title="Backend"
                        form={form}
                        field={`disciplines.${backendIndex}`}
                        valueFetch={() => backend.proficiency}
                    />
                )}

                {!!database && (
                    <Proficiency
                        title="Database"
                        form={form}
                        field={`disciplines.${databaseIndex}`}
                        valueFetch={() => database.proficiency}
                    />
                )}

                {!!devops && (
                    <Proficiency
                        title="Infrastructure / DevOps"
                        form={form}
                        field={`disciplines.${devopsIndex}`}
                        valueFetch={() => devops.proficiency}
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
                    <Proficiency
                        title={skill.skill}
                        form={form}
                        field={`skills.${index}`}
                        valueFetch={() => form.values.skills[index].proficiency}
                    />
                ))}
            </Stack>
        </Stack>
    );
};
