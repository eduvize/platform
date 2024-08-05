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
} from "@mantine/core";
import { DateInput } from "@mantine/dates";
import { UserDto } from "../../../../../models/dto";
import { ProfileUpdatePayload } from "../../../../../api/contracts/ProfileUpdatePayload";
import { memo, useRef, useState } from "react";
import UserApi from "../../../../../api/UserApi";
import {
    AdvancedPillInput,
    SpacedDivider,
} from "../../../../../components/molecules";
import AutocompleteApi from "../../../../../api/AutocompleteApi";
import { EngineeringDiscipline } from "../../../../../models/enums";
import { UseFormReturnType } from "@mantine/form";

interface BasicInfoStepProps {
    toggleStep: (step: string) => void;
    userDetails: UserDto | null;
    form: UseFormReturnType<ProfileUpdatePayload>;
    onAvatarChange: () => void;
}

export const BasicInfoStep = memo(
    ({ toggleStep, userDetails, form, onAvatarChange }: BasicInfoStepProps) => {
        const avatarInputRef = useRef<HTMLInputElement>(null);
        const [disciplines, setDisciplines] = useState<EngineeringDiscipline[]>(
            []
        );

        const handleAvatarUpload = () => {
            const file = avatarInputRef.current?.files?.[0];

            if (!file) return;

            UserApi.uploadAvatar(file).then(() => {
                onAvatarChange();
            });
        };

        const handleToggleDiscipline = (discipline: EngineeringDiscipline) => {
            if (disciplines.includes(discipline)) {
                setDisciplines(disciplines.filter((x) => x !== discipline));
            } else {
                setDisciplines([...disciplines, discipline]);
            }
        };

        console.log(form.getInputProps("programming_languages"));

        return (
            <>
                <input
                    type="file"
                    ref={avatarInputRef}
                    onChange={handleAvatarUpload}
                    accept="image/jpg, image/jpeg, image/png"
                    style={{ display: "none" }}
                />

                <SpacedDivider
                    label="Basic Information"
                    labelPosition="left"
                    labelColor="blue"
                    labelSize="lg"
                    spacePlacement="bottom"
                    spacing="sm"
                />

                <Stack gap="1em">
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
                                    radius="xl"
                                />
                            </UnstyledButton>
                        </Tooltip>
                    </Center>

                    <Space h="sm" />

                    <Stack>
                        <Group justify="space-between">
                            <Stack w="48%" gap={0}>
                                <InputLabel>First name</InputLabel>
                                <Input
                                    {...form.getInputProps("first_name")}
                                    placeholder="John"
                                />
                            </Stack>

                            <Stack w="48%" gap={0}>
                                <InputLabel>Last name</InputLabel>
                                <Input
                                    {...form.getInputProps("last_name")}
                                    placeholder="Doe"
                                />
                            </Stack>
                        </Group>

                        <Group justify="space-between">
                            <Stack w="48%" gap={0}>
                                <InputLabel>Favorite Animal</InputLabel>
                                <Input
                                    {...form.getInputProps("favorite_animal")}
                                    placeholder=""
                                />
                            </Stack>

                            <Stack w="48%" gap={0}>
                                <InputLabel>Favorite Activity</InputLabel>
                                <Input
                                    {...form.getInputProps("favorite_activity")}
                                    placeholder=""
                                />
                            </Stack>
                        </Group>

                        <DateInput
                            label="Birthdate"
                            placeholder="MM/DD/YYYY"
                            valueFormat="MM/DD/YYYY"
                        />

                        <Textarea
                            {...form.getInputProps("bio")}
                            label="Bio"
                            placeholder="Introduce yourself - what are your goals, do you like to be challenged? Give us a brief overview"
                            rows={4}
                        />
                    </Stack>
                </Stack>

                <SpacedDivider
                    label="Where are you in your journey?"
                    labelPosition="left"
                    labelColor="blue"
                    labelSize="lg"
                    spacing="sm"
                />

                <Stack gap="1em">
                    <Center>
                        <Group>
                            <Chip
                                color="green"
                                size="md"
                                onClick={() => toggleStep("hobby")}
                            >
                                I'm a hobbyist
                            </Chip>

                            <Chip
                                color="green"
                                size="md"
                                onClick={() => toggleStep("education")}
                            >
                                I am or have been a student
                            </Chip>

                            <Chip
                                color="green"
                                size="md"
                                onClick={() => toggleStep("employment")}
                            >
                                I'm working in the industry
                            </Chip>
                        </Group>
                    </Center>
                </Stack>

                <SpacedDivider
                    label="What do you specialize in?"
                    labelPosition="left"
                    labelColor="blue"
                    labelSize="lg"
                    spacing="sm"
                />

                <Stack gap="1em">
                    <Center>
                        <Group>
                            <Chip
                                color="green"
                                size="md"
                                checked={disciplines.includes(
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
                                color="green"
                                size="md"
                                checked={disciplines.includes(
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
                                color="green"
                                size="md"
                                checked={disciplines.includes(
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
                                color="green"
                                size="md"
                                checked={disciplines.includes(
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

                <SpacedDivider
                    label="What programming languages are you proficient in?"
                    labelPosition="left"
                    labelColor="blue"
                    labelSize="lg"
                    spacing="sm"
                />

                <AdvancedPillInput
                    {...form.getInputProps("programming_languages")}
                    valueFetch={(query) =>
                        AutocompleteApi.getProgrammingLanguages(query)
                    }
                />

                <SpacedDivider
                    label="Which frameworks / libraries have you worked with?"
                    labelPosition="left"
                    labelColor="blue"
                    labelSize="lg"
                    spacing="sm"
                />

                <AdvancedPillInput
                    {...form.getInputProps("libraries")}
                    valueFetch={(query) => {
                        return AutocompleteApi.getLibraries(disciplines, query);
                    }}
                />
            </>
        );
    }
);
