import { LearningCapacity } from "../enums";

export interface UserSkill {
    skill_type: number;
    skill: string;
    proficiency: number | null;
}

export interface UserProfileDto {
    first_name: string | null;
    last_name: string | null;
    bio: string | null;
    github_username: string | null;
    avatar_url: string | null;
    learning_capacities: LearningCapacity[];
    disciplines: string[];
    skills: UserSkill[];
}
