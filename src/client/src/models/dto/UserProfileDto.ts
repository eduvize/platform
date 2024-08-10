import { LearningCapacity } from "../enums";
import { SchoolDto } from "./SchoolDto";
import { EmploymentDto } from "./Employment";
import { HobbyProjectDto } from "./HobbyProjectDto";

export enum HobbyReason {
    LearnNewTechnology = "learn_new_technology",
    Entertaining = "entertaining",
    MakeMoney = "make_money",
    DiversifySkills = "diversify_skills",
    Challenging = "challenging",
    CreativeOutlet = "creative_outlet",
}

export interface UserSkillDto {
    id: string;
    skill_type: number;
    skill: string;
    proficiency: number | null;
}

export interface UserDisciplineDto {
    discipline_type: number;
    proficiency: number | null;
}

export interface HobbyDto {
    skills: string[];
    reasons: HobbyReason[];
    projects: HobbyProjectDto[];
}

export interface StudentDto {
    schools: SchoolDto[];
}

export interface ProfessionalDto {
    employers: EmploymentDto[];
}

export interface UserProfileDto {
    first_name: string | null;
    last_name: string | null;
    birthdate: string | Date | null;
    bio: string | null;
    github_username: string | null;
    avatar_url: string | null;
    learning_capacities: LearningCapacity[];
    selected_learning_capacities?: LearningCapacity[];
    disciplines: UserDisciplineDto[];
    skills: UserSkillDto[];
    hobby: HobbyDto | null;
    student: StudentDto | null;
    professional: ProfessionalDto | null;
}
