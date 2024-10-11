import { useContextSelector } from "use-context-selector";
import { OnboardingContext } from "../OnboardingContext";

export const useInstructorVisibility = () => {
    return useContextSelector(
        OnboardingContext,
        (context) => context.instructorVisible
    );
};
