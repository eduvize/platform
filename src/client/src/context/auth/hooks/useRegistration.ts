import { useState } from "react";
import { useContextSelector } from "use-context-selector";
import { AuthContext } from "@context/auth";

type RegisterFuncType = (
    email: string,
    username: string,
    password: string
) => void;

export const useRegistration = (): [
    RegisterFuncType,
    boolean,
    CallableFunction
] => {
    const register = useContextSelector(AuthContext, (v) => v.register);
    const [isFailed, setIsFailed] = useState(false);

    return [
        (email: string, username: string, password: string) => {
            return register(email, username, password).catch(() => {
                setIsFailed(true);
            });
        },
        isFailed,
        () => setIsFailed(false),
    ];
};
