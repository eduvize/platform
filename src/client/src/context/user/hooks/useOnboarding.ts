import { useContext } from "react";
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
            is_profile_complete: false,
            recently_verified: true,
        }
    );
};
