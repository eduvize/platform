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
}

export default new AuthApi("auth");
