import { ChatProvider, useChat } from "@context/chat";
import { useInstructors } from "@hooks/instructors";
import { InstructorDto } from "@models/dto";
import { useEffect, useMemo, useState } from "react";
import { createContext } from "use-context-selector";

interface Context {
    instructorVisible: boolean;
    instructor: InstructorDto | null;
    setInstructor: (instructorId: string) => void;
    sendEvent: (message: string) => void;
    setSection: (section: number) => void;
}

const defaultValues: Context = {
    instructorVisible: false,
    instructor: null,
    setInstructor: () => {},
    sendEvent: () => {},
    setSection: () => {},
};

export const OnboardingContext = createContext<Context>(defaultValues);

interface OnboardingProviderProps {
    children: React.ReactNode;
}

const Provider = ({ children }: OnboardingProviderProps) => {
    const { setInstructor, sendMessage, setPrompt } = useChat();
    const instructors = useInstructors();
    const [selectedInstructorId, setSelectedInstructorId] = useState<
        string | null
    >(null);
    const [currentSection, setCurrentSection] = useState(0);

    const instructor = useMemo(() => {
        return instructors.find((i) => i.id === selectedInstructorId);
    }, [instructors, selectedInstructorId]);

    const instructorVisible = useMemo(() => {
        return !!instructor && currentSection > 0;
    }, [instructor, currentSection]);

    const handleSetInstructor = (instructorId: string) => {
        setSelectedInstructorId(instructorId);
        setInstructor(instructorId);
    };

    const handleSendEvent = (message: string) => {
        sendMessage(`Event: ${message}`, true);
    };

    useEffect(() => {
        if (currentSection === 2) {
            setPrompt("profile-builder").then(() => {
                handleSendEvent(
                    "The user has selected you as their instructor"
                );
            });
        }
    }, [currentSection]);

    return (
        <OnboardingContext.Provider
            value={{
                instructorVisible,
                instructor: instructor ?? null,
                setInstructor: handleSetInstructor,
                sendEvent: handleSendEvent,
                setSection: setCurrentSection,
            }}
        >
            {children}
        </OnboardingContext.Provider>
    );
};

export const OnboardingProvider = ({ children }: OnboardingProviderProps) => {
    return (
        <ChatProvider prompt="onboarding">
            <Provider>{children}</Provider>
        </ChatProvider>
    );
};
