import { useEffect, useState } from "react";
import { CourseListingDto } from "@models/dto";
import { CourseApi } from "@api";

export const useCourses = () => {
    const [courses, setCourses] = useState<CourseListingDto[]>([]);

    useEffect(() => {
        if (courses.length > 0 && !courses.some((x) => x.is_generating)) return;

        const refreshInterval = setInterval(() => {
            handleLoadCourses();
        }, 5000);

        handleLoadCourses();

        return () => {
            clearInterval(refreshInterval);
        };
    }, [courses]);

    const handleLoadCourses = () => {
        CourseApi.getCourses().then(setCourses);
    };

    return courses;
};
