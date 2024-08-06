import AuthApi from "../../api/AuthApi";
import { jwtDecode } from "jwt-decode";
import { createContext } from "use-context-selector";
import { useEffect, useState } from "react";

type Context = {
    login: (email: string, password: string) => Promise<void>;
    register: (
        email: string,
        username: string,
        password: string
    ) => Promise<void>;
    isAuthenticated: boolean;
    userId: string | null;
    token: string | null;
};

const defaultValue: Context = {
    login: (email, password) => Promise.resolve(),
    register: (email, username, password) => Promise.resolve(),
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

            try {
                const decoded: any = jwtDecode(token);

                if (decoded) {
                    setUserId(decoded.id);
                }
            } catch (e) {
                console.error(e);
            }
        }
    }, []);

    const handleSetToken = (token: string) => {
        localStorage.setItem("token", token);
        setToken(token);
    };

    const handleLogin = async (email: string, password: string) => {
        return AuthApi.login(email, password).then(({ token }) => {
            handleSetToken(token);
            setIsAuthenticated(true);
        });
    };

    const handleRegister = async (
        email: string,
        username: string,
        password: string
    ) => {
        return AuthApi.register(email, username, password).then(({ token }) => {
            handleSetToken(token);
            setIsAuthenticated(true);
        });
    };

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
