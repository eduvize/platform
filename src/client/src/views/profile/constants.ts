export type ProfileStep =
    | "basic"
    | "hobby"
    | "education"
    | "professional"
    | "proficiencies";

export type ProfileHeaderInfo = {
    title: string;
    description: string;
};

export const PROFILE_HEADERS: Record<ProfileStep, ProfileHeaderInfo> = {
    basic: {
        title: "About You",
        description: `
Fill out basic information about yourself so we can get to know you a little bit better. This is high-level information that will be leveraged
in order to match you with the best courses that fit your interests and goals, and allows us to better understand your background and experience.
        `,
    },
    hobby: {
        title: "Hobbies and Interests",
        description: `
We'd like to know a little more about what drives your passion projects. Tell us about what motivates you, what technology you're using, and what projects you've poured your time into.
        `,
    },
    education: {
        title: "Education",
        description: `
Tell us about your academic background, such as where you received formal education, what area of study, and any degrees or certifications you've earned.
        `,
    },
    professional: {
        title: "Professional Experience",
        description: `
Tell us about your professional background and experience, such as where you've worked, what roles you've held, and what technologies you've worked with.
        `,
    },
    proficiencies: {
        title: "Proficiencies",
        description: `
Rate yourself on your listed skills and disciplines. This will help us better understand your comfort levels with different technologies and areas of expertise.
        `,
    },
};
