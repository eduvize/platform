import { CourseApi } from "@api";
import { Center, Loader } from "@mantine/core";
import { CourseDto } from "@models/dto";
import { useEffect, useState } from "react";
import { createContext } from "use-context-selector";

type Context = {
    course: CourseDto | null;
    markSectionCompleted: (lessonId: string, lessonIndex: number) => void;
};

const defaultValue: Context = {
    course: null,
    markSectionCompleted: () => {},
};

export const CourseContext = createContext<Context>(defaultValue);

interface CourseProviderProps {
    courseId: string;
    children: React.ReactNode;
}

export const CourseProvider = ({ courseId, children }: CourseProviderProps) => {
    const [course, setCourse] = useState<CourseDto | null>(null);

    useEffect(() => {
        CourseApi.getCourse(courseId).then((course) => {
            setCourse(course);
        });
    }, [courseId]);

    if (!course) {
        return (
            <Center h="100%">
                <Loader size="lg" type="dots" />
            </Center>
        );
    }

    const handleSectionCompletion = (lessonId: string, lessonIndex: number) => {
        if (
            lessonId !== course.current_lesson_id ||
            lessonIndex !== course.lesson_index
        ) {
            return;
        }

        CourseApi.markSectionCompleted(courseId).then((change) => {
            if (change.is_course_complete) {
                setCourse({
                    ...course,
                    completed_at_utc: new Date().toISOString(),
                });
            } else if (
                typeof change.lesson_id !== "undefined" &&
                typeof change.section_index !== "undefined"
            ) {
                setCourse({
                    ...course,
                    current_lesson_id: change.lesson_id,
                    lesson_index: change.section_index,
                });
            }
        });
    };

    return (
        <CourseContext.Provider
            value={{
                course,
                markSectionCompleted: handleSectionCompletion,
            }}
        >
            {children}
        </CourseContext.Provider>
    );
};
