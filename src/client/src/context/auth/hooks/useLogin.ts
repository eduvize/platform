import { useState } from "react";
import { useContextSelector } from "use-context-selector";
import { AuthContext } from "@context/auth";

type LoginFuncType = (email: string, password: string) => void;

export const useLogin = (): [LoginFuncType, boolean, CallableFunction] => {
    const login = useContextSelector(AuthContext, (v) => v.login);
    const [failed, setFailed] = useState(false);

    return [
        (email: string, password: string) => {
            login(email, password).catch(() => {
                setFailed(true);
            });
        },
        failed,
        () => setFailed(false),
    ];
};
