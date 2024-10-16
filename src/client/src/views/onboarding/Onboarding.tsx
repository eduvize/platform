import { CourseDto } from "@models/dto";
import { Lesson } from "@organisms";
import { Overview } from "./Overview";
import { Instructors } from "./Instructors";
import { Profile } from "./Profile";
import {
    useInstructorVisibility,
    useOnboardingFlow,
    useOnboardingInstructor,
} from "@context/onboarding/hooks";
import { useChat, useToolCallEffect } from "@context/chat";
import { ChatTool } from "@models/enums";
import { useEffect, useState } from "react";
import { Welcome } from "./Welcome";

export const Onboarding = () => {
    const { setSection } = useOnboardingFlow();
    const [sectionOverride, setSectionOverride] = useState(0);
    const { setInstructor, instructor } = useOnboardingInstructor();
    const { sendMessage, purge, setPrompt } = useChat();
    const isInstructorVisible = useInstructorVisibility();
    const [welcome, setWelcome] = useState(true);

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
                                content: (
                                    <Overview
                                        onNext={() => setSectionOverride(1)}
                                    />
                                ),
                            },
                            {
                                title: "Meet your Instructor",
                                description:
                                    "Your instructor sets the tone for your courses. Think about how you like to learn, who you like to speak with about complex subjects, and what type of approach you prefer when learning.",
                                order: 1,
                                content: (
                                    <Instructors
                                        value={instructor?.id}
                                        onNext={() => setSectionOverride(2)}
                                        onInstructorSelected={(
                                            instructorId
                                        ) => {
                                            console.log(
                                                "Instructor selected",
                                                instructorId
                                            );
                                            setInstructor(instructorId).then(
                                                () => {
                                                    purge();
                                                    sendMessage("Hello!", true);
                                                }
                                            );
                                        }}
                                    />
                                ),
                            },
                            {
                                title: "Getting to Know You",
                                description:
                                    "Walk through a series of exercises to completely customize your Eduvize experience. We want to learn about you, and how you best learn.",
                                order: 2,
                                content: <Profile />,
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

    useEffect(() => {
        setSection(sectionOverride);

        if (sectionOverride === 2) {
            setPrompt("profile-builder").then(() => {
                sendMessage(
                    "Event: The user has selected you as their instructor",
                    true
                );
            });
        } else if (sectionOverride === 1) {
            setPrompt("onboarding");
        }
    }, [sectionOverride]);

    useToolCallEffect(ChatTool.OnboardingSelectInstructor, () => {
        setSectionOverride(2);
        setPrompt("profile-builder").then(() => {
            sendMessage(
                "Event: The user has selected you as their instructor",
                true
            );
        });
    });

    if (welcome) {
        return <Welcome onGetStarted={() => setWelcome(false)} />;
    }

    return (
        <Lesson
            hideNumberedLabels
            hideInstructor={!isInstructorVisible}
            {...onboardingCourse.modules[0].lessons[0]}
            course={onboardingCourse}
            section={sectionOverride}
            onSectionChange={(section) => {
                setSectionOverride(section);
            }}
        />
    );
};
