import { useContextSelector } from "use-context-selector";
import { CourseContext } from "@context/course";
import { CourseDto } from "@models/dto";

interface UseCourseReturn {
    course: CourseDto;
    markSectionCompleted: (lessonId: string, lessonIndex: number) => void;
}

export const useCourse = (): UseCourseReturn => {
    const course = useContextSelector(CourseContext, (v) => v.course);
    const markSectionCompleted = useContextSelector(
        CourseContext,
        (v) => v.markSectionCompleted
    );

    return {
        course: course!,
        markSectionCompleted,
    };
};
