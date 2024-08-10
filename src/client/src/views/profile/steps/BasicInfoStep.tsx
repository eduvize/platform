import {
    Space,
    Stack,
    Center,
    Tooltip,
    UnstyledButton,
    Avatar,
    Group,
    InputLabel,
    Input,
    Textarea,
    Chip,
    Text,
    Button,
} from "@mantine/core";
import { DateInput } from "@mantine/dates";
import { UserDto } from "../../../models/dto";
import { ProfileUpdatePayload } from "../../../api/contracts/ProfileUpdatePayload";
import { memo, useCallback, useMemo, useRef } from "react";
import UserApi from "../../../api/UserApi";
import {
    AdvancedPillInput,
    SpacedDivider,
} from "../../../components/molecules";
import AutocompleteApi from "../../../api/AutocompleteApi";
import {
    EngineeringDiscipline,
    LearningCapacity,
    UserSkillType,
} from "../../../models/enums";
import { UseFormReturnType } from "@mantine/form";
import { ProfileStep } from "../Profile";
import { isBasicInformationComplete } from "../validation";

interface BasicInfoStepProps {
    userDetails: UserDto | null;
    form: UseFormReturnType<ProfileUpdatePayload>;
    onAvatarChange: () => void;
    onChangeStep: (step: ProfileStep) => void;
}

export const BasicInfoStep = memo(
    ({
        userDetails,
        form,
        onAvatarChange,
        onChangeStep,
    }: BasicInfoStepProps) => {
        const avatarInputRef = useRef<HTMLInputElement>(null);

        const isComplete = useMemo(
            () => isBasicInformationComplete(form),
            [form.values]
        );

        const moveNext = useCallback(() => {
            if (!isComplete) return;

            // Determine the next step
            if (
                form.values.learning_capacities.includes(LearningCapacity.Hobby)
            ) {
                onChangeStep("hobby");
            } else if (
                form.values.learning_capacities.includes(
                    LearningCapacity.Student
                )
            ) {
                onChangeStep("education");
            } else if (
                form.values.learning_capacities.includes(
                    LearningCapacity.Professional
                )
            ) {
                onChangeStep("professional");
            }
        }, [isComplete, form.values]);

        const handleAvatarUpload = () => {
            const file = avatarInputRef.current?.files?.[0];

            if (!file) return;

            UserApi.uploadAvatar(file).then(() => {
                onAvatarChange();
            });
        };

        const handleToggleDiscipline = (discipline: EngineeringDiscipline) => {
            const existing = form.values.disciplines.find(
                (x) => x.discipline_type === discipline
            );

            if (existing) {
                form.setFieldValue(
                    "disciplines",
                    form.values.disciplines.filter(
                        (x) => x.discipline_type !== discipline
                    )
                );
            } else {
                form.setFieldValue("disciplines", [
                    ...form.values.disciplines,
                    {
                        discipline_type: discipline,
                        proficiency: null,
                    },
                ]);
            }
        };

        const handleToggleLearningCapacity = (capacity: LearningCapacity) => {
            const existing = form.values.learning_capacities.includes(capacity);

            if (existing) {
                form.setFieldValue(
                    "learning_capacities",
                    form.values.learning_capacities.filter(
                        (x) => x !== capacity
                    )
                );
            } else {
                form.setFieldValue("learning_capacities", [
                    ...form.values.learning_capacities,
                    capacity,
                ]);
            }
        };

        const getDisciplineChecked = useCallback(
            (discipline: EngineeringDiscipline) => {
                return form.values.disciplines.some(
                    (x) => x.discipline_type === discipline
                );
            },
            [form.values.disciplines]
        );

        const getLearningCapacityChecked = useCallback(
            (capacity: LearningCapacity) => {
                return form.values.learning_capacities.includes(capacity);
            },
            [form.values.learning_capacities]
        );

        console.log(form.values.learning_capacities);

        return (
            <Stack>
                <input
                    type="file"
                    ref={avatarInputRef}
                    onChange={handleAvatarUpload}
                    accept="image/jpg, image/jpeg, image/png"
                    style={{ display: "none" }}
                />

                <Stack gap="md">
                    <Center>
                        <Tooltip
                            label="Upload a profile picture"
                            position="bottom"
                        >
                            <UnstyledButton
                                onClick={() => avatarInputRef.current?.click()}
                            >
                                <Avatar
                                    src={
                                        userDetails?.profile?.avatar_url ||
                                        undefined
                                    }
                                    size="10rem"
                                    radius="50%"
                                />
                            </UnstyledButton>
                        </Tooltip>
                    </Center>

                    <Space h="sm" />

                    <Stack>
                        <Group justify="space-between">
                            <Stack w="48%" gap={0}>
                                <InputLabel required>First name</InputLabel>
                                <Input
                                    {...form.getInputProps("first_name")}
                                    placeholder="John"
                                />
                            </Stack>

                            <Stack w="48%" gap={0}>
                                <InputLabel required>Last name</InputLabel>
                                <Input
                                    {...form.getInputProps("last_name")}
                                    placeholder="Doe"
                                />
                            </Stack>
                        </Group>

                        <Group justify="space-between">
                            <Stack w="48%" gap={0}>
                                <DateInput
                                    {...form.getInputProps("birthdate")}
                                    required
                                    label="Birthdate"
                                    placeholder="MM/DD/YYYY"
                                    valueFormat="MM/DD/YYYY"
                                />
                            </Stack>

                            <Stack w="48%" gap={0}>
                                <InputLabel required>
                                    Favorite Animal
                                </InputLabel>
                                <Input
                                    {...form.getInputProps("favorite_animal")}
                                    placeholder=""
                                />
                            </Stack>
                        </Group>

                        <Textarea
                            required
                            {...form.getInputProps("bio")}
                            label="Bio"
                            placeholder="Introduce yourself - what are your goals, do you like to be challenged? Give us a brief overview"
                            rows={4}
                        />
                    </Stack>
                </Stack>

                <Stack gap={0}>
                    <SpacedDivider
                        bold
                        label="Your Journey"
                        labelPosition="left"
                        labelColor="blue"
                        labelSize="lg"
                        spacePlacement="top"
                        spacing="lg"
                    />

                    <Text size="sm" c="gray" mb="md">
                        Tell us a bit about your journey as a developer.
                    </Text>

                    <Stack gap="md">
                        <Center>
                            <Group>
                                <Chip
                                    checked={getLearningCapacityChecked(
                                        LearningCapacity.Hobby
                                    )}
                                    onClick={() =>
                                        handleToggleLearningCapacity(
                                            LearningCapacity.Hobby
                                        )
                                    }
                                    color="blue"
                                    size="sm"
                                >
                                    I'm a hobbyist
                                </Chip>

                                <Chip
                                    checked={getLearningCapacityChecked(
                                        LearningCapacity.Student
                                    )}
                                    onClick={() =>
                                        handleToggleLearningCapacity(
                                            LearningCapacity.Student
                                        )
                                    }
                                    color="blue"
                                    size="sm"
                                >
                                    I am or have been a student
                                </Chip>

                                <Chip
                                    checked={getLearningCapacityChecked(
                                        LearningCapacity.Professional
                                    )}
                                    onClick={() =>
                                        handleToggleLearningCapacity(
                                            LearningCapacity.Professional
                                        )
                                    }
                                    color="blue"
                                    size="sm"
                                >
                                    I'm working in the industry
                                </Chip>
                            </Group>
                        </Center>
                    </Stack>
                </Stack>

                <Stack gap={0}>
                    <SpacedDivider
                        bold
                        label="Tech Stack"
                        labelPosition="left"
                        labelColor="blue"
                        labelSize="lg"
                        spacePlacement="top"
                        spacing="lg"
                    />

                    <Text size="sm" c="gray" mb="md">
                        What parts of the stack do you involve yourself with?
                    </Text>

                    <Stack gap="md">
                        <Center>
                            <Group>
                                <Chip
                                    color="blue"
                                    size="sm"
                                    checked={getDisciplineChecked(
                                        EngineeringDiscipline.Frontend
                                    )}
                                    onClick={() =>
                                        handleToggleDiscipline(
                                            EngineeringDiscipline.Frontend
                                        )
                                    }
                                >
                                    Frontend
                                </Chip>

                                <Chip
                                    color="blue"
                                    size="sm"
                                    checked={getDisciplineChecked(
                                        EngineeringDiscipline.Backend
                                    )}
                                    onClick={() =>
                                        handleToggleDiscipline(
                                            EngineeringDiscipline.Backend
                                        )
                                    }
                                >
                                    Backend
                                </Chip>

                                <Chip
                                    color="blue"
                                    size="sm"
                                    checked={getDisciplineChecked(
                                        EngineeringDiscipline.Database
                                    )}
                                    onClick={() =>
                                        handleToggleDiscipline(
                                            EngineeringDiscipline.Database
                                        )
                                    }
                                >
                                    Database
                                </Chip>

                                <Chip
                                    color="blue"
                                    size="sm"
                                    checked={getDisciplineChecked(
                                        EngineeringDiscipline.DevOps
                                    )}
                                    onClick={() =>
                                        handleToggleDiscipline(
                                            EngineeringDiscipline.DevOps
                                        )
                                    }
                                >
                                    Infrastructure / DevOps
                                </Chip>
                            </Group>
                        </Center>
                    </Stack>
                </Stack>

                <Stack gap={0}>
                    <SpacedDivider
                        bold
                        label="Programming Languages"
                        labelPosition="left"
                        labelColor="blue"
                        labelSize="lg"
                        spacePlacement="top"
                        spacing="lg"
                    />

                    <Text size="sm" c="gray" mb="lg">
                        What languages have you worked with?
                    </Text>

                    <AdvancedPillInput
                        {...form.getInputProps("skills")}
                        placeholder="Type to search for a language"
                        valueFetch={(query) =>
                            AutocompleteApi.getProgrammingLanguages(
                                form.values.disciplines.map(
                                    (d) => d.discipline_type
                                ),
                                query
                            )
                        }
                        valueSelector={(x) => x.skill}
                        valueFilter={(x) => x.skill_type === 1}
                        valueMapper={(x) => {
                            const existing = form.values.skills.find(
                                (l) => l.skill === x
                            );

                            return {
                                skill_type: existing ? existing.skill_type : 1,
                                skill: x,
                                proficiency: existing
                                    ? existing.proficiency
                                    : null,
                            };
                        }}
                        disabled={form.values.disciplines.length === 0}
                    />
                </Stack>

                <Stack gap={0}>
                    <SpacedDivider
                        bold
                        label="Frameworks / Libraries"
                        labelPosition="left"
                        labelColor="blue"
                        labelSize="lg"
                        spacePlacement="top"
                        spacing="lg"
                    />

                    <Text size="sm" c="gray" mb="lg">
                        What libraries and frameworks have you worked with?
                    </Text>

                    <AdvancedPillInput
                        {...form.getInputProps("skills")}
                        placeholder="Type to search for a library or framework"
                        valueFetch={(query) => {
                            const disciplineTypes = form.values.disciplines.map(
                                (x) => x.discipline_type
                            );
                            const disciplineNames = disciplineTypes.map(
                                (x) => EngineeringDiscipline[x]
                            );

                            return AutocompleteApi.getLibraries(
                                disciplineNames,
                                form.values.skills
                                    .filter(
                                        (s) =>
                                            s.skill_type ===
                                            UserSkillType.ProgrammingLanguage
                                    )
                                    .map((s) => s.skill),
                                query
                            );
                        }}
                        valueSelector={(x) => x.skill}
                        valueFilter={(x) => x.skill_type === 2}
                        valueMapper={(x) => {
                            const existing = form.values.skills.find(
                                (l) => l.skill === x
                            );

                            return {
                                skill_type: existing ? existing.skill_type : 2,
                                skill: x,
                                proficiency: existing
                                    ? existing.proficiency
                                    : null,
                            };
                        }}
                        disabled={
                            form.values.skills.filter(
                                (s) =>
                                    s.skill_type ===
                                    UserSkillType.ProgrammingLanguage
                            ).length === 0 &&
                            form.values.disciplines.length === 0
                        }
                    />
                </Stack>

                <Space h="lg" />

                <Button
                    variant="gradient"
                    disabled={!isComplete}
                    onClick={moveNext}
                >
                    Continue
                </Button>
            </Stack>
        );
    }
);
