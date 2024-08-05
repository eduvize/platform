import { AuthContext } from "../AuthContext";
import { useContextSelector } from "use-context-selector";

export const useCurrentUserId = () => {
    const userId = useContextSelector(AuthContext, (v) => v.userId);

    return userId;
};
