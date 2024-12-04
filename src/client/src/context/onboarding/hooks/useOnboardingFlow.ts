import { useContextSelector } from "use-context-selector";
import { OnboardingContext } from "../OnboardingContext";

export const useOnboardingFlow = () => {
    const setSection = useContextSelector(
        OnboardingContext,
        (context) => context.setSection
    );

    return {
        setSection,
    };
};
