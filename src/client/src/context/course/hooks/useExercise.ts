import { useContextSelector } from "use-context-selector";
import { CourseContext } from "../CourseContext";
import { Exercise } from "@models/dto";

export const useExercise = (exerciseId: string): Exercise | null => {
    const course = useContextSelector(CourseContext, (v) => v.course);

    const allExercises =
        course?.modules.flatMap((module) =>
            module.lessons.flatMap((lesson) => lesson.exercises)
        ) ?? [];

    return allExercises.find((exercise) => exercise.id === exerciseId) ?? null;
};
