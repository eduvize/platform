import { CourseDto } from "@models/dto";
import { Lesson } from "@organisms";

export const Onboarding = () => {
    const onboardingCourse: CourseDto = {
        id: "onboarding",
        title: "Onboarding",
        description: "Onboarding course description",
        cover_image_url: "",
        current_lesson_id: "",
        created_at_utc: new Date().toISOString(),
        modules: [
            {
                order: 0,
                title: "Setup",
                description: "Setup module",
                lessons: [
                    {
                        id: "setup-1",
                        title: "Setup 1",
                        description: "Setup lesson 1",
                        sections: [
                            {
                                title: "Setup section 1",
                                description: "Setup section 1",
                                order: 0,
                                content: "Setup section 1",
                            },
                        ],
                        order: 0,
                        exercises: [],
                    },
                ],
            },
        ],
    };

    return (
        <Lesson
            {...onboardingCourse.modules[0].lessons[0]}
            course={onboardingCourse}
        />
    );
};
