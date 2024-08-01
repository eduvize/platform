import BaseApi from "./BaseApi";

class AuthApi extends BaseApi {
    public login(email: string, password: string): Promise<string> {
        return this.post("/api/auth/login", { email, password });
    }

    public register(
        email: string,
        username: string,
        password: string
    ): Promise<string> {
        return this.post("/api/auth/register", { email, username, password });
    }
}

export default new AuthApi();
