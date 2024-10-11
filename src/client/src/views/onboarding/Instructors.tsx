import { useInstructors } from "@hooks/instructors";
import { Group, Stack, Text, Title } from "@mantine/core";
import { SelectableInstructor } from "@molecules";
import { useEffect, useMemo, useState } from "react";

export const Instructors = () => {
    const instructors = useInstructors();
    const [selectedInstructorId, setSelectedInstructorId] = useState<
        string | null
    >(null);
    const selectedInstructor = useMemo(() => {
        return instructors.find(
            (instructor) => instructor.id === selectedInstructorId
        );
    }, [instructors, selectedInstructorId]);
    const selectedInstructorIndex = useMemo(() => {
        return instructors.findIndex(
            (instructor) => instructor.id === selectedInstructorId
        );
    }, [instructors, selectedInstructorId]);

    useEffect(() => {
        if (!instructors.length) return;

        setSelectedInstructorId(instructors[0].id);
    }, [instructors]);

    return (
        <Stack pt="xl" gap="lg">
            <Title order={2} fw={400} c="white">
                Choose your instructor.
            </Title>

            <Text>
                Your instructor sets the tone for your courses. Think about how
                you like to learn, who you like to speak with about complex
                subjects, and what type of approach you prefer when learning.
                Don’t worry though, you can change your instructor at any time,
                even in the middle of a course. If you want to test them out,
                you can chat with them in the{" "}
                <span style={{ color: "#51CF66", fontWeight: "bold" }}>
                    Instructor Window
                </span>{" "}
                on the right.
            </Text>

            <Group>
                {instructors.map((instructor) => (
                    <SelectableInstructor
                        key={instructor.id}
                        {...instructor}
                        selected={selectedInstructorId === instructor.id}
                        onClick={() => setSelectedInstructorId(instructor.id)}
                    />
                ))}
            </Group>

            <Title order={3} fw={400} c="white">
                Instructor {selectedInstructorIndex + 1}:{" "}
                {selectedInstructor?.name} - {selectedInstructor?.alias}
            </Title>
        </Stack>
    );
};
