import {
    Group,
    Text,
    Stack,
    Chip,
    AccordionItem,
    Accordion,
    ActionIcon,
    Center,
    Box,
} from "@mantine/core";
import { IconEditCircle, IconX } from "@tabler/icons-react";
import { SpacedDivider } from "../../molecules/layout";
import { UserSkillType } from "../../../models/enums";
import { UseFormReturnType } from "@mantine/form";
import { ProfileUpdatePayload } from "../../../api/contracts";
import { ReactNode, useMemo, useRef, useState } from "react";

interface ProfileAccordionProps {
    index: number;
    title: string;
    form: UseFormReturnType<ProfileUpdatePayload>;
    titleField: string;
    skillField?: string;
    validationFunc?: () => boolean;
    component: ReactNode;
    onRemove?: () => void;
}

export const ProfileAccordion = (props: ProfileAccordionProps) => {
    const {
        index,
        title,
        form,
        titleField,
        skillField,
        validationFunc,
        component,
        onRemove,
    } = props;
    const nameRef = useRef<HTMLDivElement>(null);
    const [showNameEdit, setShowNameEdit] = useState(false);
    const [editingName, setEditingName] = useState(false);

    const handleEditName = () => {
        setEditingName(true);

        setTimeout(() => {
            if (nameRef.current) {
                nameRef.current.focus();

                // Select all text
                const range = document.createRange();
                range.selectNodeContents(nameRef.current);
                const selection = window.getSelection();
                selection?.removeAllRanges();
                selection?.addRange(range);
            }
        }, 100);
    };

    const handleBlurChange = () => {
        setEditingName(false);

        form.setFieldValue(titleField, nameRef.current?.textContent || "");
    };

    const isValid = useMemo(() => {
        if (!validationFunc) return true;

        return validationFunc();
    }, [form.values, validationFunc]);

    return (
        <AccordionItem key={title} value={title}>
            <Center>
                <Accordion.Control>
                    <Box
                        onMouseOver={() => setShowNameEdit(true)}
                        onMouseOut={() => setShowNameEdit(false)}
                    >
                        <Group>
                            <Text
                                size="lg"
                                c={isValid ? "gray" : "yellow"}
                                contentEditable={editingName}
                                onBlur={handleBlurChange}
                                ref={nameRef}
                                style={{ outline: "none" }}
                            >
                                {title}
                            </Text>

                            {showNameEdit && !editingName && (
                                <ActionIcon
                                    size="sm"
                                    variant="subtle"
                                    color="gray"
                                    onClick={handleEditName}
                                >
                                    <IconEditCircle />
                                </ActionIcon>
                            )}
                        </Group>
                    </Box>
                </Accordion.Control>

                <ActionIcon
                    size="lg"
                    variant="subtle"
                    color="gray"
                    onClick={onRemove}
                >
                    <IconX />
                </ActionIcon>
            </Center>

            <Accordion.Panel>
                <Stack>
                    {component}

                    {skillField && (
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

                            <Text c="gray" size="sm" mb="lg">
                                Which programming languages did you study with?
                            </Text>

                            <Group>
                                {form.values.skills
                                    .filter(
                                        (x) =>
                                            x.skill_type ===
                                            UserSkillType.ProgrammingLanguage
                                    )
                                    .map((language) => (
                                        <Chip
                                            {...form.getInputProps(skillField, {
                                                type: "checkbox",
                                                value: language.skill,
                                            })}
                                            c="blue"
                                        >
                                            {language.skill}
                                        </Chip>
                                    ))}
                            </Group>
                        </Stack>
                    )}

                    {skillField && (
                        <Stack gap={0}>
                            <SpacedDivider
                                bold
                                label="Libraries / Frameworks"
                                labelPosition="left"
                                labelColor="blue"
                                labelSize="lg"
                                spacePlacement="top"
                                spacing="lg"
                            />

                            <Text c="gray" size="sm" mb="lg">
                                Select any libraries or frameworks you used
                                during this time.
                            </Text>

                            <Group>
                                {form.values.skills
                                    .filter(
                                        (x) =>
                                            x.skill_type ===
                                            UserSkillType.Library
                                    )
                                    .map((lib) => (
                                        <Chip
                                            {...form.getInputProps(skillField, {
                                                type: "checkbox",
                                                value: lib.skill,
                                            })}
                                            c="blue"
                                        >
                                            {lib.skill}
                                        </Chip>
                                    ))}
                            </Group>
                        </Stack>
                    )}
                </Stack>
            </Accordion.Panel>
        </AccordionItem>
    );
};
