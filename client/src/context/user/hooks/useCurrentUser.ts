import { useEffect, useState } from "react";
import { UserDto } from "../../../models/dto";
import { UserContext } from "../UserContext";
import UserApi from "../../../api/UserApi";
import { useContextSelector } from "use-context-selector";

export const useCurrentUser = (): [UserDto | null, CallableFunction] => {
    const userDetails = useContextSelector(UserContext, (v) => v.userDetails);
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
