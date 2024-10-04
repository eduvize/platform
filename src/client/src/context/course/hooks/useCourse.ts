import { useContextSelector } from "use-context-selector";
import { CourseContext } from "@context/course";
import { CourseDto } from "@models/dto";

interface UseCourseReturn {
    course: CourseDto;
    markLessonComplete: (lessonId: string) => void;
}

export const useCourse = (): UseCourseReturn => {
    const course = useContextSelector(CourseContext, (v) => v.course);
    const markLessonComplete = useContextSelector(
        CourseContext,
        (v) => v.markLessonComplete
    );

    return {
        course: course!,
        markLessonComplete,
    };
};
