import { useContext } from "react";
import { UserContext } from "../UserContext";

export const useOnboarding = () => {
    const { onboardingStatus } = useContext(UserContext);

    return (
        onboardingStatus || {
            is_verified: false,
            is_profile_complete: false,
            recently_verified: true,
        }
    );
};
