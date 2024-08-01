import { useContext } from "react";
import { AuthContext } from "../AuthContext";

export const useAuthenticated = () => {
    const { isAuthenticated } = useContext(AuthContext);

    return isAuthenticated;
};
