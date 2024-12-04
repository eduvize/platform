import { useContextSelector } from "use-context-selector";
import { CourseContext } from "@context/course";
import { CourseDto } from "@models/dto";

interface UseCourseReturn {
    course: CourseDto;
    markLessonComplete: (lessonId: string) => void;
    markSectionComplete: (lessonId: string, sectionIndex: number) => void;
}

export const useCourse = (): UseCourseReturn => {
    const course = useContextSelector(CourseContext, (v) => v.course);
    const markLessonComplete = useContextSelector(
        CourseContext,
        (v) => v.markLessonComplete
    );
    const markSectionComplete = useContextSelector(
        CourseContext,
        (v) => v.markSectionComplete
    );

    return {
        course: course!,
        markLessonComplete,
        markSectionComplete,
    };
};
