import { useEffect, useState } from "react";
import { UserDto } from "../../../models/dto/profile";
import { UserContext } from "../UserContext";
import UserApi from "../../../api/UserApi";
import { useContextSelector } from "use-context-selector";
import { ProfileUpdatePayload } from "../../../api/contracts";

export const useCurrentUser = (): [
    UserDto | null,
    CallableFunction,
    (profile: ProfileUpdatePayload) => void
] => {
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
        (profile: ProfileUpdatePayload) => {
            UserApi.updateProfile(profile);
        },
    ];
};
