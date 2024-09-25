import { useContextSelector } from "use-context-selector";
import { ExerciseContext } from "../ExerciseContext";

export const useExercise = () => {
    const exercise = useContextSelector(ExerciseContext, (x) => x.exercise);

    return exercise;
};
