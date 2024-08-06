import { LearningCapacity } from "../enums";
import { HobbyProjectDto } from "./HobbyProjectDto";

export enum HobbyReason {
    LearnNewTechnology = "learn_new_technology",
    Entertaining = "entertaining",
    MakeMoney = "make_money",
    DiversifySkills = "diversify_skills",
    Challenging = "challenging",
    CreativeOutlet = "creative_outlet",
}

export interface UserSkill {
    skill_type: number;
    skill: string;
    proficiency: number | null;
}

export interface HobbyDto {
    reasons: HobbyReason[];
    projects: HobbyProjectDto[];
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
    hobby: HobbyDto | null;
}
