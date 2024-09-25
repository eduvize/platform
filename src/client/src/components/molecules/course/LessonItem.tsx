import { useExercise, useExerciseObjectives } from "@context/exercise/hooks";
import { Card, Text, Stepper, Group, RingProgress } from "@mantine/core";
import { LessonDto } from "@models/dto";
import { IconHammer } from "@tabler/icons-react";

interface LessonItemProps extends LessonDto {
    active?: boolean;
    activeSection: number;
    onSectionChange: (section: number) => void;
}

export const LessonItem = ({
    active,
    title,
    description,
    sections,
    exercises,
    activeSection,
    order,
    onSectionChange,
}: LessonItemProps) => {
    const objectives = useExerciseObjectives();

    return (
        <Card withBorder>
            <Text>
                Lesson {order + 1}: {title}
            </Text>
            {active && (
                <>
                    <Text size="xs" c="dimmed">
                        {description}
                    </Text>
                    <Stepper
                        mt="lg"
                        orientation="vertical"
                        onStepClick={onSectionChange}
                        active={
                            activeSection +
                            (objectives.length > 0 &&
                            objectives.every((x) => x.is_completed)
                                ? 1
                                : 0)
                        }
                    >
                        {sections.map((section, index) => (
                            <Stepper.Step
                                key={index}
                                label={section.title}
                                description={section.description}
                                styles={{
                                    stepLabel: {
                                        fontSize: 12,
                                    },
                                }}
                            />
                        ))}

                        {exercises.length > 0 &&
                            exercises.map((exercise, index) => (
                                <Stepper.Step
                                    key={index}
                                    label="Exercise"
                                    description={
                                        <>
                                            {exercise.title}

                                            <Group gap="xs" mt="sm">
                                                <RingProgress
                                                    sections={[
                                                        {
                                                            value:
                                                                (objectives.filter(
                                                                    (x) =>
                                                                        x.is_completed
                                                                ).length /
                                                                    exercise
                                                                        .objectives
                                                                        .length) *
                                                                100,
                                                            color: "green",
                                                        },
                                                    ]}
                                                    size={28}
                                                    thickness={3}
                                                />

                                                <Text size="xs" c="green">
                                                    {
                                                        objectives.filter(
                                                            (x) =>
                                                                x.is_completed
                                                        ).length
                                                    }
                                                    /{objectives.length} tasks
                                                    completed
                                                </Text>
                                            </Group>
                                        </>
                                    }
                                    icon={<IconHammer />}
                                    styles={{
                                        stepLabel: {
                                            fontSize: 12,
                                        },
                                    }}
                                />
                            ))}
                    </Stepper>
                </>
            )}
        </Card>
    );
};
