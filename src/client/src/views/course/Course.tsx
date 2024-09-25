import { useParams } from "react-router-dom";
import { CourseProvider } from "@context/course";
import { Space } from "@mantine/core";
import { useCourse } from "@context/course/hooks";
import { useDocumentTitle } from "@mantine/hooks";
import { CourseOverview } from "@organisms";

const Component = () => {
    const { course } = useCourse();
    useDocumentTitle(`${course.title} | Eduvize`);

    return <CourseOverview />;
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
