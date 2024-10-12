import { useContextSelector } from "use-context-selector";
import { OnboardingContext } from "../OnboardingContext";
import { ChatContext } from "@context/chat";

export const useOnboardingInstructor = () => {
    const setInstructor = useContextSelector(
        ChatContext,
        (context) => context.setInstructor
    );
    const instructor = useContextSelector(
        OnboardingContext,
        (context) => context.instructor
    );

    return {
        setInstructor,
        instructor,
    };
};
