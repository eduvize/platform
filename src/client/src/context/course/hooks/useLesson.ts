import { LessonDto } from "@models/dto";
import { useContextSelector } from "use-context-selector";
import { CourseContext } from "../CourseContext";

export const useLesson = (id: string): LessonDto => {
    const course = useContextSelector(CourseContext, (x) => x.course);

    if (!course) throw new Error("Course not loaded");

    const lesson = course.modules
        .flatMap((x) => x.lessons)
        .find((x) => x.id === id);

    if (!lesson) throw new Error("Lesson not found");

    return lesson;
};
