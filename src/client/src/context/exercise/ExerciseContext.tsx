import { useCourse } from "@context/course/hooks";
import { PlaygroundProvider } from "@context/playground";
import { Exercise, ExerciseObjective } from "@models/dto";
import { useEffect, useMemo, useState } from "react";
import { createContext } from "use-context-selector";

type Context = {
    objectives: ExerciseObjective[];
    exercise: Exercise | null;
};

const defaultValue: Context = {
    exercise: null,
    objectives: [],
};

export const ExerciseContext = createContext<Context>(defaultValue);

interface ExerciseProviderProps {
    lessonId: string;
    children: React.ReactNode;
}

export const ExerciseProvider = ({
    lessonId,
    children,
}: ExerciseProviderProps) => {
    const { course } = useCourse();
    const [objectives, setObjectives] = useState<ExerciseObjective[]>([]);

    const lesson = useMemo(() => {
        if (!course) return null;

        return course.modules
            .flatMap((x) => x.lessons)
            .find((x) => x.id === lessonId);
    }, [course, lessonId]);

    useEffect(() => {
        if (!lesson) return;

        const objectives = lesson.exercises.flatMap((x) => x.objectives);

        setObjectives(objectives);
    }, []);

    if (!lesson || !lesson.exercises.length) {
        return children;
    }

    const exercise = lesson.exercises[0];

    return (
        <ExerciseContext.Provider
            value={{
                exercise,
                objectives,
            }}
        >
            <PlaygroundProvider
                environmentId={exercise.environment_id}
                onExerciseObjectiveStatusChange={(objectiveId, status) => {
                    setObjectives((prev) =>
                        prev.map((x) =>
                            x.id === objectiveId
                                ? { ...x, is_completed: status }
                                : x
                        )
                    );
                }}
                readme={<></>}
            >
                {children}
            </PlaygroundProvider>
        </ExerciseContext.Provider>
    );
};
