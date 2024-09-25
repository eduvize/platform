import { CourseApi } from "@api";
import { Center, Loader } from "@mantine/core";
import { CourseDto } from "@models/dto";
import { useEffect, useState } from "react";
import { createContext } from "use-context-selector";

type Context = {
    course: CourseDto | null;
    markLessonComplete: (lessonId: string) => void;
    setObjectiveStatus: (objectiveId: string, status: boolean) => void;
};

const defaultValue: Context = {
    course: null,
    markLessonComplete: () => {},
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
                });
            }
        });
    };

    return (
        <CourseContext.Provider
            value={{
                course,
                markLessonComplete,
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
