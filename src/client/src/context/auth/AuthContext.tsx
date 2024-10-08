import { useEffect, useRef, useState } from "react";
import { jwtDecode } from "jwt-decode";
import { createContext } from "use-context-selector";
import { AuthApi } from "@api";
import { Center, Loader } from "@mantine/core";
import { OAuthProvider } from "@models/enums";
const githubClientId = import.meta.env.VITE_GITHUB_CLIENT_ID;
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

type Context = {
    login: (email: string, password: string) => Promise<void>;
    oauthRedirect: (provider: OAuthProvider) => void;
    oauthExchange: (code: string) => void;
    register: (
        email: string,
        username: string,
        password: string
    ) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
    userId: string | null;
};

const defaultValue: Context = {
    login: () => Promise.resolve(),
    oauthRedirect: () => {},
    oauthExchange: () => {},
    register: () => Promise.resolve(),
    logout: () => {},
    isAuthenticated: false,
    userId: null,
};

export const AuthContext = createContext<Context>(defaultValue);

interface AuthProviderProps {
    children: React.ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
    const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(
        null
    );
    const [userId, setUserId] = useState<string | null>(null);

    useEffect(() => {
        const token = localStorage.getItem("token");

        if (token) {
            try {
                const decoded: any = jwtDecode(token);

                if (decoded) {
                    setUserId(decoded.id);

                    if (decoded.exp * 1000 < Date.now()) {
                        handleRefresh();
                    } else {
                        handleSetRefreshTimeout(
                            (decoded.exp * 1000 - Date.now()) / 1000
                        );

                        setIsAuthenticated(true);
                    }
                }
            } catch (e) {
                setIsAuthenticated(false);
            }
        } else {
            setIsAuthenticated(false);
        }

        return () => {
            if (refreshTimeoutRef.current)
                clearTimeout(refreshTimeoutRef.current);
        };
    }, []);

    const handleSetRefreshTimeout = (expiresInSeconds: number) => {
        if (refreshTimeoutRef.current) {
            clearTimeout(refreshTimeoutRef.current);
        }

        refreshTimeoutRef.current = setTimeout(
            () => handleRefresh(),
            expiresInSeconds * 1000
        );
    };

    const handleRefresh = () => {
        const refreshToken = localStorage.getItem("refreshToken");

        if (!refreshToken) {
            if (localStorage.getItem("token")) {
                localStorage.removeItem("token");
                window.location.reload();
            }

            return;
        }

        AuthApi.getRefreshedToken(refreshToken)
            .then(({ access_token, refresh_token, expires_in }) => {
                handleSetTokens(access_token, refresh_token);

                const decoded: any = jwtDecode(access_token);

                if (decoded.exp) {
                    if (refreshTimeoutRef.current) {
                        clearTimeout(refreshTimeoutRef.current);
                    }

                    handleSetRefreshTimeout(expires_in);
                }

                setIsAuthenticated(true);
            })
            .catch(() => {
                if (localStorage.getItem("token")) {
                    localStorage.removeItem("token");
                    localStorage.removeItem("refreshToken");
                    window.location.reload();
                }
            });
    };

    const handleSetTokens = (accessToken: string, refreshToken: string) => {
        localStorage.setItem("token", accessToken);
        localStorage.setItem("refreshToken", refreshToken);
    };

    const handleLogin = async (email: string, password: string) => {
        return AuthApi.login(email, password)
            .then(({ access_token, refresh_token, expires_in }) => {
                handleSetTokens(access_token, refresh_token);
                handleSetRefreshTimeout(expires_in);
                setIsAuthenticated(true);
            })
            .catch(() => {
                setIsAuthenticated(false);
            });
    };

    const handleOAuthRedirect = (provider: OAuthProvider) => {
        localStorage.setItem("oauth_provider", provider);

        const redirectUrl = window.location.href.split("?")[0];

        switch (provider) {
            case OAuthProvider.Github: {
                window.location.href = `https://github.com/login/oauth/authorize?client_id=${githubClientId}&scope=user:email`;
                break;
            }

            case OAuthProvider.Google: {
                window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${googleClientId}&redirect_uri=${redirectUrl}&response_type=code&scope=email%20profile`;
            }
        }
    };

    const handleOAuthCodeExchange = (code: string) => {
        const provider = localStorage.getItem("oauth_provider");

        if (!provider) return;

        AuthApi.exchangeOAuthCode(provider as OAuthProvider, code).then(
            ({ access_token, refresh_token, expires_in }) => {
                handleSetTokens(access_token, refresh_token);
                handleSetRefreshTimeout(expires_in);
                setIsAuthenticated(true);

                const currentUrlWithoutQs = window.location.href.split("?")[0];
                window.history.replaceState(
                    {},
                    document.title,
                    currentUrlWithoutQs
                );
            }
        );
    };

    const handleRegister = async (
        email: string,
        username: string,
        password: string
    ) => {
        return AuthApi.register(email, username, password).then(
            ({ access_token, refresh_token, expires_in }) => {
                handleSetTokens(access_token, refresh_token);
                handleSetRefreshTimeout(expires_in);
                setIsAuthenticated(true);
            }
        );
    };

    const handleLogout = () => {
        AuthApi.logout().finally(() => {
            localStorage.removeItem("token");
            localStorage.removeItem("refreshToken");
            setIsAuthenticated(false);
        });
    };

    if (isAuthenticated === null) {
        return (
            <Center h="100vh">
                <Loader type="dots" size="xl" />
            </Center>
        );
    }

    return (
        <AuthContext.Provider
            value={{
                login: handleLogin,
                oauthRedirect: handleOAuthRedirect,
                oauthExchange: handleOAuthCodeExchange,
                register: handleRegister,
                logout: handleLogout,
                isAuthenticated,
                userId,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};
