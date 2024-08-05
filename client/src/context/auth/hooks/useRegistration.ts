import { useState } from "react";
import { AuthContext } from "../AuthContext";
import { useContextSelector } from "use-context-selector";

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
