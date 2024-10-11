import { ChatProvider } from "@context/chat";
import { CourseProvider } from "@context/course";
import { ExerciseProvider } from "@context/exercise";
import { useEffect, memo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Lesson as LessonComponent } from "@organisms";
import { useCourse, useLesson } from "@context/course/hooks";

export const Lesson = () => {
    const params = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        if (!params.course_id || !params.lesson_id) {
            navigate("/dashboard/courses");
        }
    }, []);

    if (!params.course_id || !params.lesson_id) {
        return null;
    }

    const Wrapper = memo(() => {
        const { course } = useCourse();
        const lesson = useLesson(params.lesson_id!);

        return <LessonComponent {...lesson} course={course} />;
    });

    return (
        <CourseProvider courseId={params.course_id}>
            <ExerciseProvider lessonId={params.lesson_id}>
                <ChatProvider prompt="lesson" resourceId={params.lesson_id}>
                    <Wrapper />
                </ChatProvider>
            </ExerciseProvider>
        </CourseProvider>
    );
};
