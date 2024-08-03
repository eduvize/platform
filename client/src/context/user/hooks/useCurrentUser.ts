import { useContext } from "react";
import { UserDto } from "../../../models/dto";
import { UserContext } from "../UserContext";

export const useCurrentUser = (): UserDto | null => {
    const { userDetails } = useContext(UserContext);

    return userDetails;
};
