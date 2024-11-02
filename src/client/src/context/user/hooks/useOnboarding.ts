import { UserContext } from "../UserContext";
import { useContextSelector } from "use-context-selector";

export const useOnboarding = () => {
    const onboardingStatus = useContextSelector(
        UserContext,
        (v) => v.onboardingStatus
    );

    return (
        onboardingStatus || {
            is_verified: false,
            is_first_course_created: false,
            recently_verified: true,
        }
    );
};
