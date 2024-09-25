import { useContextSelector } from "use-context-selector";
import { ExerciseContext } from "../ExerciseContext";

export const useExerciseObjectives = () => {
    const objectives = useContextSelector(ExerciseContext, (x) => x.objectives);

    return objectives;
};
