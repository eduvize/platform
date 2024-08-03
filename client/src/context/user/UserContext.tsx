import { createContext, useEffect, useState } from "react";
import { useCurrentUserId } from "../auth";
import { UserDto } from "../../models/dto";
import UserApi from "../../api/UserApi";

type Context = {
    userDetails: UserDto | null;
};

const defaultValue: Context = {
    userDetails: null,
};

export const UserContext = createContext<Context>(defaultValue);

interface UserProviderProps {
    children: React.ReactNode;
}

export const UserProvider = ({ children }: UserProviderProps) => {
    const id = useCurrentUserId();
    const [userDetails, setUserDetails] = useState<UserDto | null>(null);

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
    }, [id]);

    return (
        <UserContext.Provider
            value={{
                userDetails,
            }}
        >
            {children}
        </UserContext.Provider>
    );
};
