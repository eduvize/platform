import { UserDto } from "../models/dto";
import BaseApi from "./BaseApi";

class UserApi extends BaseApi {
    getCurrentUser() {
        return this.get<UserDto>("/users/me");
    }
}

export default new UserApi();
