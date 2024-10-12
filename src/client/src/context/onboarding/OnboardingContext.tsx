import { useChat } from "@context/chat";
import { useInstructors } from "@hooks/instructors";
import { InstructorDto } from "@models/dto";
import { useEffect, useMemo, useState } from "react";
import { createContext } from "use-context-selector";

interface Context {
    instructorVisible: boolean;
    instructor: InstructorDto | null;
    sendEvent: (message: string) => void;
    setSection: (section: number) => void;
}

const defaultValues: Context = {
    instructorVisible: false,
    instructor: null,
    sendEvent: () => {},
    setSection: () => {},
};

export const OnboardingContext = createContext<Context>(defaultValues);

interface OnboardingProviderProps {
    children: React.ReactNode;
}

export const OnboardingProvider = ({ children }: OnboardingProviderProps) => {
    const instructors = useInstructors();
    const [currentSection, setCurrentSection] = useState(0);
    const { setInstructor, sendMessage, setPrompt, instructorId } = useChat({
        prompt:
            currentSection === 1
                ? "onboarding"
                : currentSection === 2
                ? "profile-builder"
                : undefined,
    });

    const instructor = useMemo(() => {
        return instructors.find((i) => i.id === instructorId);
    }, [instructors, instructorId]);

    const instructorVisible = useMemo(() => {
        return !!instructor && currentSection > 0;
    }, [instructor, currentSection]);

    const handleSendEvent = (message: string) => {
        sendMessage(`Event: ${message}`, true);
    };

    return (
        <OnboardingContext.Provider
            value={{
                instructorVisible,
                instructor: instructor ?? null,
                sendEvent: handleSendEvent,
                setSection: setCurrentSection,
            }}
        >
            {children}
        </OnboardingContext.Provider>
    );
};
