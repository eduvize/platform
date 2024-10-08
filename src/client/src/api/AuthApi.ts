import { OAuthProvider } from "@models/enums";
import BaseApi from "./BaseApi";
import { TokenResponse } from "@contracts";

class AuthApi extends BaseApi {
    login(email: string, password: string): Promise<TokenResponse> {
        return this.post("login", { email, password });
    }

    register(
        email: string,
        username: string,
        password: string
    ): Promise<TokenResponse> {
        return this.post("register", { email, username, password });
    }

    exchangeOAuthCode(
        provider: OAuthProvider,
        code: string
    ): Promise<TokenResponse> {
        return this.post(`oauth/${provider}`, { code });
    }

    logout(): Promise<void> {
        return this.deleteWithPayload("", {
            refresh_token: localStorage.getItem("refreshToken"),
        });
    }
}

export default new AuthApi("auth");
