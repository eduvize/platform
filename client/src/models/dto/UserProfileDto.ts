import { LearningCapacity } from "../enums";

export interface UserProgrammingLanguage {
    name: string;
    proficiency: number | null;
}

export interface UserLibrary {
    name: string;
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
    programming_languages: UserProgrammingLanguage[];
    libraries: UserLibrary[];
}
