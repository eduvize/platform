import { useContextSelector } from "use-context-selector";
import { AuthContext } from "@context/auth";

export const useAuthenticated = () => {
    const isAuthenticated = useContextSelector(
        AuthContext,
        (v) => v.isAuthenticated
    );

    return isAuthenticated;
};
