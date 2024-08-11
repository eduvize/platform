import { LearningCapacity } from "../../enums";
import { HobbyDto } from "./HobbyDto";
import { ProfessionalDto } from "./ProfessionalDto";
import { StudentDto } from "./StudentDto";
import { UserDisciplineDto } from "./UserDisciplineDto";
import { UserSkillDto } from "./UserSkillDto";

export interface UserProfileDto {
    first_name: string | null;
    last_name: string | null;
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
