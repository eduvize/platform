export enum QuizType {
    MultipleChoice = "multiple_choice",
    ShortAnswer = "short_answer",
}

export interface Quiz {
    title: string;
    description: string;
    quiz_type: QuizType;
}
