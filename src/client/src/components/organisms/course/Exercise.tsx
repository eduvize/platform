import { useExercise } from "@context/course/hooks";
import { PlaygroundProvider } from "@context/playground";
import { Box, Checkbox, List, ListItem, Space, Text } from "@mantine/core";
import { Playground } from "../playground";
import { memo, useState } from "react";

interface ExerciseProps {
    exerciseId: string;
}

export const Exercise = ({ exerciseId }: ExerciseProps) => {
    const exercise = useExercise(exerciseId);
    const [completedObjectives, setCompletedObjectives] = useState<string[]>(
        []
    );

    if (!exercise) {
        return null;
    }

    const Readme = memo(
        ({ completedObjectives }: { completedObjectives: string[] }) => {
            return (
                <>
                    <Text size="xl">{exercise.title}</Text>
                    <Text size="sm">{exercise.summary}</Text>

                    <Space h="xl" />
                    <Text size="lg">Task List</Text>
                    <Text size="sm">
                        Complete the following objectives to finish this
                        exercise. If you need assistance, please ask your
                        instructor.
                    </Text>
                    <List mt="sm" listStyleType="none">
                        {exercise.objectives.map(({ id, objective }) => (
                            <ListItem>
                                <Checkbox
                                    label={objective}
                                    checked={completedObjectives.includes(id)}
                                    mb="sm"
                                />
                            </ListItem>
                        ))}
                    </List>
                </>
            );
        },
        (prevProps, nextProps) => {
            return (
                prevProps.completedObjectives === nextProps.completedObjectives
            );
        }
    );

    return (
        <Box>
            <PlaygroundProvider
                environmentId={exercise.environment_id}
                onExerciseObjectiveStatusChange={(objectiveId, isCompleted) => {
                    if (isCompleted) {
                        setCompletedObjectives((prev) => [
                            ...prev,
                            objectiveId,
                        ]);
                    } else {
                        setCompletedObjectives((prev) =>
                            prev.filter((id) => id !== objectiveId)
                        );
                    }
                }}
                readme={<Readme completedObjectives={completedObjectives} />}
            >
                <Playground height="800px" />
            </PlaygroundProvider>
        </Box>
    );
};
