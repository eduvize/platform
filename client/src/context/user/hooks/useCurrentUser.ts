import { useContext, useEffect, useState } from "react";
import { UserDto } from "../../../models/dto";
import { UserContext } from "../UserContext";
import UserApi from "../../../api/UserApi";

export const useCurrentUser = (): [UserDto | null, CallableFunction] => {
    const { userDetails } = useContext(UserContext);
    const [cachedDetails, setCachedDetails] = useState<UserDto | null>(
        userDetails
    );

    useEffect(() => {
        setCachedDetails(userDetails);
    }, [userDetails]);

    return [
        cachedDetails,
        () => {
            UserApi.getCurrentUser().then((user) => {
                setCachedDetails(user);
            });
        },
    ];
};
