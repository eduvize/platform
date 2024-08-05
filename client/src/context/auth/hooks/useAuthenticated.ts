import { AuthContext } from "../AuthContext";
import { useContextSelector } from "use-context-selector";

export const useAuthenticated = () => {
    const isAuthenticated = useContextSelector(
        AuthContext,
        (v) => v.isAuthenticated
    );

    return isAuthenticated;
};
