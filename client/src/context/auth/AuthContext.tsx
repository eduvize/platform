import AuthApi from "../../api/AuthApi";
import { jwtDecode } from "jwt-decode";
import { createContext, useEffect, useState } from "react";

type Context = {
    login: (email: string, password: string) => void;
    register: (email: string, username: string, password: string) => void;
    isAuthenticated: boolean;
    userId: string | null;
    token: string | null;
};

const defaultValue: Context = {
    login: (email, password) => {},
    register: (email, username, password) => {},
    isAuthenticated: false,
    userId: null,
    token: null,
};

export const AuthContext = createContext<Context>(defaultValue);

interface AuthProviderProps {
    children: React.ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [userId, setUserId] = useState<string | null>(null);
    const [token, setToken] = useState<string | null>(null);

    useEffect(() => {
        const token = localStorage.getItem("token");

        if (token) {
            setToken(token);
            setIsAuthenticated(true);

            const decoded: any = jwtDecode(token);

            if (decoded) {
                setUserId(decoded.id);
            }
        }
    }, []);

    const handleSetToken = (token: string) => {
        localStorage.setItem("token", token);
        setToken(token);
    };

    const handleLogin = async (email: string, password: string) => {
        AuthApi.login(email, password)
            .then(({ token }: any) => {
                handleSetToken(token);
                setIsAuthenticated(true);
            })
            .catch((error) => {
                console.error(error);
            });
    };

    const handleRegister = async (
        email: string,
        username: string,
        password: string
    ) => {};

    return (
        <AuthContext.Provider
            value={{
                login: handleLogin,
                register: handleRegister,
                isAuthenticated,
                userId,
                token,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};
