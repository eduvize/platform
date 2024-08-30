import { Section } from "./Section";

export interface LessonDto {
    id: string;
    title: string;
    description: string;
    order: number;
    sections: Section[];
    is_completed: boolean;
}
