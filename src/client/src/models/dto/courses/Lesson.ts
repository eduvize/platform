import { Section } from "./Section";

export interface LessonDto {
    title: string;
    description: string;
    sections: Section[];
}
