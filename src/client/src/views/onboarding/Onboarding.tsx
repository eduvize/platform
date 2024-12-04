import { CourseDto } from "@models/dto";
import { Lesson } from "@organisms";
import { Overview } from "./Overview";
import { Instructors } from "./Instructors";
import { Profile } from "./Profile";
import {
    useOnboardingFlow,
    useOnboardingInstructor,
} from "@context/onboarding/hooks";
import { useChat, useToolCallEffect } from "@context/chat";
import { ChatTool } from "@models/enums";
import { useEffect, useState } from "react";
import { Welcome } from "./Welcome";
import { FirstCourse } from "./FirstCourse";

export const Onboarding = () => {
    const { setSection } = useOnboardingFlow();
    const [sectionOverride, setSectionOverride] = useState(0);
    const { setInstructor, instructor } = useOnboardingInstructor();
    const { sendMessage, purge, setPrompt } = useChat();
    const [welcome, setWelcome] = useState(true);
    const [isProfileComplete, setIsProfileComplete] = useState(false);

    const onboardingCourse: CourseDto = {
        id: "onboarding",
        title: "Onboarding",
        description: "Onboarding course description",
        cover_image_url: "",
        current_lesson_id: "",
        current_section_index: 0,
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
                                            setInstructor(instructorId).then();
                                        }}
                                    />
                                ),
                            },
                            {
                                title: "Getting to Know You",
                                description:
                                    "Walk through a series of exercises to completely customize your Eduvize experience. We want to learn about you, and how you best learn.",
                                order: 2,
                                content: (
                                    <Profile
                                        onNext={() => setSectionOverride(3)}
                                    />
                                ),
                            },
                            {
                                title: "Your First Course",
                                description:
                                    "To build a Course, we'll start by talking to your instructor about what you want to learn.",
                                order: 3,
                                content: <FirstCourse />,
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

        switch (sectionOverride) {
            case 1:
                setPrompt("onboarding").then(() => {
                    sendMessage("Hello!", true);
                });
                break;
            case 2:
                setPrompt("profile-builder").then(() => {
                    sendMessage(
                        "Event: The user has selected you as their instructor",
                        true
                    );
                });
                break;
            case 3:
                setPrompt("course-creation").then(() => {
                    sendMessage(
                        "Hello! I'd like to get started on my first course.",
                        true
                    );
                });
                break;
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

    useToolCallEffect(ChatTool.ProfileBuilderSetProfileComplete, () => {
        setIsProfileComplete(true);
    });

    if (welcome) {
        return <Welcome onGetStarted={() => setWelcome(false)} />;
    }

    console.log(`WHAT THE FUCK NUTS IS THIS SHIT`, sectionOverride);

    return (
        <Lesson
            controlled
            hideNumberedLabels
            hideInstructor={sectionOverride === 0}
            {...onboardingCourse.modules[0].lessons[0]}
            course={onboardingCourse}
            section={sectionOverride}
            onSectionChange={(section) => {
                setSectionOverride(section);

                return true;
            }}
        />
    );
};
