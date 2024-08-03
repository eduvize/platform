import { UserDto, UserOnboardingStatusDto } from "../models/dto";
import BaseApi from "./BaseApi";

class UserApi extends BaseApi {
    getCurrentUser() {
        return this.get<UserDto>("me");
    }

    getOnboardingStatus() {
        return this.get<UserOnboardingStatusDto>("me/onboarding");
    }
}

export default new UserApi("users");
