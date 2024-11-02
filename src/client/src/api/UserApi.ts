import BaseApi from "./BaseApi";
import { FileUploadResponse } from "@contracts";
import { UserDto, UserOnboardingStatusDto } from "@models/dto";

class UserApi extends BaseApi {
    getCurrentUser() {
        return this.get<UserDto>("me");
    }

    getOnboardingStatus() {
        return this.get<UserOnboardingStatusDto>("me/onboarding");
    }

    uploadAvatar(file: File) {
        const data = new FormData();
        data.append("file", file);
        return this.postForm<FileUploadResponse>("me/profile/avatar", data);
    }
}

export default new UserApi("users");
