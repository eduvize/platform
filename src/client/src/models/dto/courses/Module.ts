import { LessonDto } from "./Lesson";

export interface ModuleDto {
    title: string;
    description: string;
    lessons: LessonDto[];
}
