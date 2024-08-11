import { useEffect, useState } from "react";
import { useContextSelector } from "use-context-selector";
import { UserApi } from "@api";
import { ProfileUpdatePayload } from "@contracts";
import { UserContext } from "@context/user";
import { UserDto } from "@models/dto";

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
