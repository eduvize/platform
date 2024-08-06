import { AuthContext } from "../AuthContext";
import { useContextSelector } from "use-context-selector";

export const useAuthToken = () => {
    const token = useContextSelector(AuthContext, (v) => v.token);

    return token;
};
