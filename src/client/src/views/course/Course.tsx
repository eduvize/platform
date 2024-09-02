import { useParams } from "react-router-dom";
import { CourseProvider } from "@context/course";
import { Space } from "@mantine/core";
import { useCourse } from "@context/course/hooks";
import { useDocumentTitle } from "@mantine/hooks";
import { Lesson, CourseOverview } from "@organisms";
import { ChatProvider } from "@context/chat";

const Component = () => {
    const params = useParams();
    const { course } = useCourse();
    useDocumentTitle(`${course.title} | Eduvize`);

    if (params.lesson_id)
        return (
            <Lesson
                courseId={params.course_id as string}
                lessonId={params.lesson_id}
            />
        );

    return <CourseOverview />;
};

export const Course = () => {
    const params = useParams();

    return (
        <CourseProvider courseId={params.course_id as string}>
            <ChatProvider>
                <Component />
            </ChatProvider>

            <Space h="xl" />
        </CourseProvider>
    );
};
