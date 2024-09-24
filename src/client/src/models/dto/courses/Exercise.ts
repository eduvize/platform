export interface ExerciseObjective {
    id: string;
    objective: string;
}

export interface Exercise {
    id: string;
    title: string;
    summary: string;
    environment_id: string;
    objectives: ExerciseObjective[];
}
