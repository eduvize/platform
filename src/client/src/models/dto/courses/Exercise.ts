export interface ExerciseObjective {
    id: string;
    objective: string;
    description: string;
    is_completed: boolean;
}

export interface Exercise {
    id: string;
    title: string;
    summary: string;
    environment_id: string;
    objectives: ExerciseObjective[];
}
