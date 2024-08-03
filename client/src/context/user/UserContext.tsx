import { createContext, useEffect, useState } from "react";
import { useCurrentUserId } from "../auth";
import { UserDto, UserOnboardingStatusDto } from "../../models/dto";
import UserApi from "../../api/UserApi";

type Context = {
    userDetails: UserDto | null;
    onboardingStatus: UserOnboardingStatusDto | null;
};

const defaultValue: Context = {
    userDetails: null,
    onboardingStatus: null,
};

export const UserContext = createContext<Context>(defaultValue);

interface UserProviderProps {
    children: React.ReactNode;
}

export const UserProvider = ({ children }: UserProviderProps) => {
    const id = useCurrentUserId();
    const [userDetails, setUserDetails] = useState<UserDto | null>(null);
    const [onboardingStatus, setOnboardingStatus] =
        useState<UserOnboardingStatusDto | null>(null);

    useEffect(() => {
        if (!id) {
            setUserDetails(null);
        }

        UserApi.getCurrentUser()
            .then((user) => {
                setUserDetails(user);
            })
            .catch(() => {
                setUserDetails(null);
            });

        UserApi.getOnboardingStatus()
            .then((status) => {
                setOnboardingStatus(status);
            })
            .catch(() => {
                setOnboardingStatus(null);
            });
    }, [id]);

    return (
        <UserContext.Provider
            value={{
                userDetails,
                onboardingStatus,
            }}
        >
            {children}
        </UserContext.Provider>
    );
};
