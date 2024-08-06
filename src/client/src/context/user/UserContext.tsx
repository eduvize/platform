import { createContext } from "use-context-selector";
import { useEffect, useState } from "react";
import { useCurrentUserId } from "../auth";
import { UserDto, UserOnboardingStatusDto } from "../../models/dto";
import { notifications } from "@mantine/notifications";
import UserApi from "../../api/UserApi";
import { IconCheck } from "@tabler/icons-react";

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

                if (status.recently_verified) {
                    notifications.show({
                        id: "recently-verified",
                        withCloseButton: true,
                        autoClose: 5000,
                        title: "Account verified",
                        message: "Your account has been verified successfully",
                        color: "green",
                        icon: <IconCheck />,
                        loading: false,
                    });
                }
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
