import { useContext, useState } from "react";
import { AuthContext } from "../AuthContext";

type LoginFuncType = (email: string, password: string) => void;

export const useLogin = (): [LoginFuncType, boolean, CallableFunction] => {
    const { login } = useContext(AuthContext);
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
