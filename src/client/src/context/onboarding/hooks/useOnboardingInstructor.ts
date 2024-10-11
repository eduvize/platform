import { useContextSelector } from "use-context-selector";
import { OnboardingContext } from "../OnboardingContext";

export const useOnboardingInstructor = () => {
    const setInstructor = useContextSelector(
        OnboardingContext,
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
