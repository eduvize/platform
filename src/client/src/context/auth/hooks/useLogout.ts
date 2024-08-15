import { useContextSelector } from "use-context-selector";
import { AuthContext } from "@context/auth";

export const useLogout = () => {
    const logout = useContextSelector(AuthContext, (v) => v.logout);

    return logout;
};
