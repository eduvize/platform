import { ChatProvider } from "@context/chat";
import { CourseDto } from "@models/dto";
import { Lesson } from "@organisms";
import { Overview } from "./Overview";
import { useMemo, useState } from "react";
import { Instructors } from "./Instructors";

export const Onboarding = () => {
    const [currentSection, setCurrentSection] = useState(0);
    const [selectedInstructorId, setSelectedInstructorId] = useState<
        string | null
    >(null);

    const isInstructorVisible =
        currentSection > 0 && selectedInstructorId !== null;

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
                title: "Welcome to Eduvize",
                description: "",
                lessons: [
                    {
                        id: "setup-1",
                        title: "Get Ready for Your First Course",
                        description:
                            "Walk through a series of exercises to completely customize your Eduvize experience. We want to learn about you, and how you best learn.",
                        sections: [
                            {
                                title: "Overview",
                                description:
                                    "Get to know Eduvize and how to set up a course.",
                                order: 0,
                                content: <Overview />,
                            },
                            {
                                title: "Meet your Instructor",
                                description:
                                    "Your instructor sets the tone for your courses. Think about how you like to learn, who you like to speak with about complex subjects, and what type of approach you prefer when learning.",
                                order: 1,
                                content: (
                                    <Instructors
                                        onInstructorSelected={
                                            setSelectedInstructorId
                                        }
                                    />
                                ),
                            },
                            {
                                title: "Getting to Know You",
                                description:
                                    "Walk through a series of exercises to completely customize your Eduvize experience. We want to learn about you, and how you best learn.",
                                order: 2,
                                content: "Setup section 3",
                            },
                            {
                                title: "Your First Course",
                                description:
                                    "To build a Course, we'll start by talking to your instructor about what you want to learn.",
                                order: 3,
                                content: "Setup section 4",
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
        <ChatProvider
            prompt="onboarding"
            resourceId={selectedInstructorId || undefined}
        >
            <Lesson
                hideNumberedLabels
                hideInstructor={!isInstructorVisible}
                {...onboardingCourse.modules[0].lessons[0]}
                course={onboardingCourse}
                onSectionChange={(section) => {
                    setCurrentSection(section);
                }}
            />
        </ChatProvider>
    );
};
