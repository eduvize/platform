import { useContextSelector } from "use-context-selector";
import { AuthContext } from "@context/auth";

export const useCurrentUserId = () => {
    const userId = useContextSelector(AuthContext, (v) => v.userId);

    return userId;
};
