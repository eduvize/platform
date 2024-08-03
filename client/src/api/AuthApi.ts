import BaseApi from "./BaseApi";
import { TokenResponse } from "./contracts";

class AuthApi extends BaseApi {
    public login(email: string, password: string): Promise<TokenResponse> {
        return this.post("/auth/login", { email, password });
    }

    public register(
        email: string,
        username: string,
        password: string
    ): Promise<TokenResponse> {
        return this.post("/auth/register", { email, username, password });
    }
}

export default new AuthApi();
