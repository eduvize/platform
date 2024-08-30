import { CourseDto } from "@models/dto";

export const getCumulativeLessonIndex = (
    course: CourseDto,
    lessonId: string
) => {
    let cumulativeLessonIndex = 0;

    for (const module of course.modules) {
        for (const lesson of module.lessons) {
            if (lesson.id === lessonId) {
                return cumulativeLessonIndex;
            }

            cumulativeLessonIndex++;
        }
    }

    return cumulativeLessonIndex;
};
