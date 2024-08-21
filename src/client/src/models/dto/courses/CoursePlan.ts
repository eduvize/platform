import {
    CourseMaterial,
    CourseMotivation,
    CurrentSubjectExperience,
} from "@models/enums";

export interface CoursePlan {
    subject: string;
    motivations: CourseMotivation[];
    other_motivation_details?: string;
    experience: CurrentSubjectExperience | null;
    experience_details?: string;
    materials: CourseMaterial[];
}
