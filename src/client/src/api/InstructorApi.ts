import { InstructorDto } from "@models/dto";
import BaseApi from "./BaseApi";

class InstructorApi extends BaseApi {
    async getInstructors(): Promise<InstructorDto[]> {
        return await this.get<InstructorDto[]>("");
    }
}

export default new InstructorApi("instructors");
