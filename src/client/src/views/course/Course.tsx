import { useParams } from "react-router-dom";
import { CourseProvider } from "@context/course";
import { Modules } from "./Modules";
import { Lesson } from "./Lesson";
import { Space } from "@mantine/core";
import { useCourse } from "@context/course/hooks";
import { useDocumentTitle } from "@mantine/hooks";

const Component = () => {
    const params = useParams();
    const course = useCourse();
    useDocumentTitle(`${course.title} | Eduvize`);

    if (params.lesson_id)
        return (
            <Lesson
                courseId={params.course_id as string}
                lessonId={params.lesson_id}
            />
        );

    return <Modules />;
};

export const Course = () => {
    const params = useParams();

    return (
        <CourseProvider courseId={params.course_id as string}>
            <Component />

            <Space h="xl" />
        </CourseProvider>
    );
};
