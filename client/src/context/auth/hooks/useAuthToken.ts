import { useContext } from "react";
import { AuthContext } from "../AuthContext";

export const useAuthToken = () => {
    const { token } = useContext(AuthContext);

    return token;
};
