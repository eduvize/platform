import { Section } from "./Section";

export interface LessonDto {
    id: string;
    title: string;
    description: string;
    sections: Section[];
    is_completed: boolean;
}
