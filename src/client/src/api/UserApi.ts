import {
    UserDto,
    UserOnboardingStatusDto,
    UserProfileDto,
} from "../models/dto/profile";
import BaseApi from "./BaseApi";
import { FileUploadResponse } from "./contracts";
import { ProfileUpdatePayload } from "./contracts/ProfileUpdatePayload";

class UserApi extends BaseApi {
    getCurrentUser() {
        return this.get<UserDto>("me");
    }

    getOnboardingStatus() {
        return this.get<UserOnboardingStatusDto>("me/onboarding");
    }

    updateProfile(data: Partial<ProfileUpdatePayload>) {
        return this.put<UserProfileDto>("me/profile", data);
    }

    uploadAvatar(file: File) {
        const data = new FormData();
        data.append("file", file);
        return this.postForm<FileUploadResponse>("me/profile/avatar", data);
    }
}

export default new UserApi("users");
