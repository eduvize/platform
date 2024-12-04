import BaseApi from "./BaseApi";
import { ResumeScanDto } from "@models/dto";

class FileApi extends BaseApi {
    getResumeInsights = (file: File): Promise<ResumeScanDto> => {
        const formData = new FormData();
        formData.append("file", file);

        return this.postForm<ResumeScanDto>("resume", formData);
    };
}

export default new FileApi("files");
