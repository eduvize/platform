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
    programming_languages: UserProgrammingLanguage[];
    libraries: UserLibrary[];
}
