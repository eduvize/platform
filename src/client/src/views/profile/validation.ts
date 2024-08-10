import { UseFormReturnType } from "@mantine/form";
import { ProfileUpdatePayload } from "../../api/contracts";
import { UserSkillType } from "../../models/enums";

export const isBasicInformationComplete = (
    form: UseFormReturnType<ProfileUpdatePayload>
) => {
    const languages = form.values.skills.filter(
        (s) => s.skill_type === UserSkillType.ProgrammingLanguage
    );

    const libraries = form.values.skills.filter(
        (s) => s.skill_type === UserSkillType.Library
    );

    return (
        form.values.first_name &&
        form.values.last_name &&
        form.values.birthdate &&
        form.values.bio &&
        form.values.learning_capacities.length > 0 &&
        form.values.disciplines.length > 0 &&
        languages.length > 0 &&
        libraries.length > 0
    );
};

export const isHobbyInformationComplete = (
    form: UseFormReturnType<ProfileUpdatePayload>
) => {
    if (!form.values.hobby) return true;

    const languages = form.values.skills.filter(
        (s) => s.skill_type === UserSkillType.ProgrammingLanguage
    );

    const libraries = form.values.skills.filter(
        (s) => s.skill_type === UserSkillType.Library
    );

    const hobbyLanguages = form.values.hobby.skills.filter((s) =>
        languages.some((l) => l.skill === s)
    );

    const hobbyLibraries = form.values.hobby.skills.filter((s) =>
        libraries.some((l) => l.skill === s)
    );

    return (
        form.values.hobby.reasons.length > 0 &&
        hobbyLanguages.length > 0 &&
        hobbyLibraries.length > 0
    );
};

export const isEducationInformationComplete = (
    form: UseFormReturnType<ProfileUpdatePayload>
) => {
    if (!form.values.student) return true;

    const schools = form.values.student?.schools || [];

    return (
        schools.length > 0 &&
        schools.every((school) => {
            return school.school_name && school.focus;
        })
    );
};

export const isProfessionalInformationComplete = (
    form: UseFormReturnType<ProfileUpdatePayload>
) => {
    if (!form.values.professional) return true;

    const employers = form.values.professional?.employers || [];

    return (
        employers.length > 0 &&
        employers.every((employer) => {
            return (
                employer.company_name &&
                employer.position &&
                employer.description
            );
        })
    );
};
