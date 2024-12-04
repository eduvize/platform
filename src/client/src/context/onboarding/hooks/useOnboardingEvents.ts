import { useContextSelector } from "use-context-selector";
import { OnboardingContext } from "../OnboardingContext";

export const useOnboardingEvents = () => {
    const { sendEvent } = useContextSelector(OnboardingContext, (v) => ({
        sendEvent: v.sendEvent,
    }));

    return { sendEvent };
};
