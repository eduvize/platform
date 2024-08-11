import BaseApi from "./BaseApi";
import { UserProfileDto } from "@models/dto";

class FileApi extends BaseApi {
    getProfileFromResume = (file: File): Promise<UserProfileDto> => {
        const formData = new FormData();
        formData.append("file", file);

        return this.postForm<UserProfileDto>("resume", formData);
    };
}

export default new FileApi("files");
