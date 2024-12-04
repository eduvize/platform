import { CourseApi } from "@api";
import { Center, Loader } from "@mantine/core";
import { CourseDto } from "@models/dto";
import { useEffect, useState } from "react";
import { createContext } from "use-context-selector";

type Context = {
    course: CourseDto | null;
    markSectionComplete: (lessonId: string, sectionIndex: number) => void;
    markLessonComplete: (lessonId: string) => void;
    setObjectiveStatus: (objectiveId: string, status: boolean) => void;
};

const defaultValue: Context = {
    course: null,
    markLessonComplete: () => {},
    markSectionComplete: () => {},
    setObjectiveStatus: () => {},
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

    const markLessonComplete = (lessonId: string) => {
        if (lessonId !== course.current_lesson_id) {
            return;
        }

        CourseApi.markLessonComplete(courseId, lessonId).then((change) => {
            if (change.is_course_complete) {
                setCourse({
                    ...course,
                    completed_at_utc: new Date().toISOString(),
                });
            } else if (typeof change.lesson_id !== "undefined") {
                setCourse({
                    ...course,
                    current_lesson_id: change.lesson_id,
                    current_section_index: 0,
                });
            }
        });
    };

    const markSectionComplete = (lessonId: string, sectionIndex: number) => {
        if (!course) return;

        const currentLessonId = course.current_lesson_id;
        const currentSectionIndex = course.current_section_index;

        const currentLessonModule = course.modules.find((m) =>
            m.lessons.some((l) => l.id === currentLessonId)
        );

        if (!currentLessonModule) return;

        const lessonModule = course.modules.find((m) =>
            m.lessons.some((l) => l.id === lessonId)
        );

        if (!lessonModule) return;

        // If the current lesson module comes after the active lesson module, skip
        if (currentLessonModule?.order !== lessonModule?.order) {
            return;
        }

        const currentLessonIndex = currentLessonModule.lessons.findIndex(
            (l) => l.id === currentLessonId
        );
        const lessonIndex = lessonModule.lessons.findIndex(
            (l) => l.id === lessonId
        );

        // If the current lesson index is greater than the lesson index, skip
        if (
            currentLessonIndex > lessonIndex ||
            currentSectionIndex > sectionIndex
        ) {
            return;
        }

        CourseApi.markSectionComplete(courseId, lessonId, sectionIndex);
    };

    return (
        <CourseContext.Provider
            value={{
                course,
                markLessonComplete,
                markSectionComplete,
                setObjectiveStatus: (objectiveId, status) => {
                    if (!course) {
                        return;
                    }

                    const newCourse = {
                        ...course,
                        modules: course.modules.map((module) => ({
                            ...module,
                            lessons: module.lessons.map((lesson) => ({
                                ...lesson,
                                exercises: lesson.exercises.map((exercise) => ({
                                    ...exercise,
                                    objectives: exercise.objectives.map(
                                        (objective) =>
                                            objective.id === objectiveId
                                                ? {
                                                      ...objective,
                                                      is_completed: status,
                                                  }
                                                : objective
                                    ),
                                })),
                            })),
                        })),
                    };

                    setCourse(newCourse);
                },
            }}
        >
            {children}
        </CourseContext.Provider>
    );
};
