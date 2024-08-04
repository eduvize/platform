import {
    Divider,
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
    Text,
    Chip,
    PillsInput,
    Pill,
} from "@mantine/core";
import { DateInput } from "@mantine/dates";
import { UserDto } from "../../../../../models/dto";
import { ProfileUpdatePayload } from "../../../../../api/contracts/ProfileUpdatePayload";
import { useRef, useState } from "react";
import UserApi from "../../../../../api/UserApi";
import {
    AdvancedPillInput,
    SpacedDivider,
} from "../../../../../components/molecules";
import { IconX } from "@tabler/icons-react";

interface BasicInfoStepProps {
    toggleStep: (step: string) => void;
    userDetails: UserDto | null;
    values: ProfileUpdatePayload;
    onChange: (value: Partial<ProfileUpdatePayload>) => void;
    onAvatarChange: () => void;
}

export const BasicInfoStep = ({
    toggleStep,
    userDetails,
    values,
    onChange,
    onAvatarChange,
}: BasicInfoStepProps) => {
    const avatarInputRef = useRef<HTMLInputElement>(null);

    const handleAvatarUpload = () => {
        const file = avatarInputRef.current?.files?.[0];

        if (!file) return;

        UserApi.uploadAvatar(file).then(() => {
            onAvatarChange();
        });
    };

    const handleMergeProgrammingLanguages = (languages: string[]) => {
        const updatedLanguages = [...values.programming_languages];

        languages.forEach((language) => {
            if (!updatedLanguages.find((x) => x.name === language)) {
                updatedLanguages.push({ name: language, proficiency: null });
            }
        });

        updatedLanguages.forEach((language) => {
            if (!languages.includes(language.name)) {
                updatedLanguages.splice(
                    updatedLanguages.findIndex((x) => x.name === language.name),
                    1
                );
            }
        });

        onChange({ programming_languages: updatedLanguages });
    };

    const handleMergeLibraries = (libraries: string[]) => {
        const updatedLibraries = [...values.libraries];

        libraries.forEach((library) => {
            if (!updatedLibraries.find((x) => x.name === library)) {
                updatedLibraries.push({ name: library, proficiency: null });
            }
        });

        updatedLibraries.forEach((library) => {
            if (!libraries.includes(library.name)) {
                updatedLibraries.splice(
                    updatedLibraries.findIndex((x) => x.name === library.name),
                    1
                );
            }
        });

        onChange({ libraries: updatedLibraries });
    };

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
                    <Tooltip label="Upload a profile picture" position="bottom">
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
                                placeholder="John"
                                value={values.first_name || ""}
                                onChange={(event) =>
                                    onChange({
                                        first_name: event.currentTarget.value,
                                    })
                                }
                            />
                        </Stack>

                        <Stack w="48%" gap={0}>
                            <InputLabel>Last name</InputLabel>
                            <Input
                                placeholder="Doe"
                                value={values.last_name || ""}
                                onChange={(event) =>
                                    onChange({
                                        last_name: event.currentTarget.value,
                                    })
                                }
                            />
                        </Stack>
                    </Group>

                    <Group justify="space-between">
                        <Stack w="48%" gap={0}>
                            <InputLabel>Favorite Animal</InputLabel>
                            <Input
                                placeholder=""
                                value={values.first_name || ""}
                                onChange={(event) =>
                                    onChange({
                                        first_name: event.currentTarget.value,
                                    })
                                }
                            />
                        </Stack>

                        <Stack w="48%" gap={0}>
                            <InputLabel>Favorite Activity</InputLabel>
                            <Input
                                placeholder=""
                                value={values.last_name || ""}
                                onChange={(event) =>
                                    onChange({
                                        last_name: event.currentTarget.value,
                                    })
                                }
                            />
                        </Stack>
                    </Group>

                    <DateInput
                        label="Birthdate"
                        placeholder="MM/DD/YYYY"
                        valueFormat="MM/DD/YYYY"
                    />

                    <Textarea
                        label="Bio"
                        placeholder="Introduce yourself - what are your goals, do you like to be challenged? Give us a brief overview"
                        value={values.bio || ""}
                        onChange={(event) =>
                            onChange({
                                bio: event.currentTarget.value,
                            })
                        }
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
                            onClick={() => toggleStep("hobby")}
                        >
                            Frontend
                        </Chip>

                        <Chip
                            color="green"
                            size="md"
                            onClick={() => toggleStep("education")}
                        >
                            Backend
                        </Chip>

                        <Chip
                            color="green"
                            size="md"
                            onClick={() => toggleStep("employment")}
                        >
                            Database
                        </Chip>

                        <Chip
                            color="green"
                            size="md"
                            onClick={() => toggleStep("employment")}
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
                values={values.programming_languages.map((x) => x.name)}
                onChange={handleMergeProgrammingLanguages}
            />

            <SpacedDivider
                label="Which frameworks / libraries have you worked with?"
                labelPosition="left"
                labelColor="blue"
                labelSize="lg"
                spacing="sm"
            />

            <AdvancedPillInput
                values={values.libraries.map((x) => x.name)}
                onChange={handleMergeLibraries}
            />
        </>
    );
};
