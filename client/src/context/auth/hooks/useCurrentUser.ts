import { useContext } from "react";
import { AuthContext } from "../AuthContext";

export const useCurrentUser = () => {
    const { userId } = useContext(AuthContext);

    return userId;
};
