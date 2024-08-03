import { useContext, useState } from "react";
import { AuthContext } from "../AuthContext";

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
    const { register } = useContext(AuthContext);
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
