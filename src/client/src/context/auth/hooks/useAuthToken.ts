import { useContextSelector } from "use-context-selector";
import { AuthContext } from "@context/auth";

export const useAuthToken = () => {
    const token = useContextSelector(AuthContext, (v) => v.token);

    return token;
};
