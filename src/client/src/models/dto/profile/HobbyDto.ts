export enum HobbyReason {
    LearnNewTechnology = "learn_new_technology",
    Entertaining = "entertaining",
    MakeMoney = "make_money",
    DiversifySkills = "diversify_skills",
    Challenging = "challenging",
    CreativeOutlet = "creative_outlet",
}

export interface HobbyDto {
    skills: string[];
    reasons: HobbyReason[];
    projects: HobbyProjectDto[];
}

export interface HobbyProjectDto {
    project_name: string;
    description?: string;
    purpose?: string;
}
