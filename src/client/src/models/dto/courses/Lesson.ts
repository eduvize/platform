import { Exercise } from "./Exercise";
import { Section } from "./Section";

export interface LessonDto {
    id: string;
    title: string;
    description: string;
    order: number;
    sections: Section[];
    exercises: Exercise[];
}
