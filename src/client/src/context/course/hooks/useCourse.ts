import { useContextSelector } from "use-context-selector";
import { CourseContext } from "@context/course";

export const useCourse = () => {
    const course = useContextSelector(CourseContext, (v) => v.course);

    return course!;
};
