import { useContext } from "react";
import { AuthContext } from "../AuthContext";

export const useCurrentUserId = () => {
    const { userId } = useContext(AuthContext);

    return userId;
};
