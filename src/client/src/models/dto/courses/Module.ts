import { Lesson } from "./Lesson";
import { Quiz } from "./Quiz";

export interface Module {
    title: string;
    description: string;
    lessons: Lesson[];

    quiz: Quiz | null;
}
