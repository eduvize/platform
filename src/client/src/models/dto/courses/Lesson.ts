import { Exercise } from "./Exercise";

export interface Lesson {
    title: string;
    description: string;

    exercise: Exercise | null;
}
