import BaseApi from "./BaseApi";
import { InstructorDto } from "@models/dto";

class InstructorApi extends BaseApi {
    generateInstructor(animal: string) {
        return this.get<InstructorDto>(`generate?animal=${animal}`);
    }

    getInstructor() {
        return this.get<InstructorDto>("");
    }

    approve(): Promise<void> {
        return this.post("approve", {});
    }
}

export default new InstructorApi("instructor");
