import BaseApi from "./BaseApi";
import { AdditionalInputsDto, CoursePlan as CoursePlanDto } from "@models/dto";

class CourseApi extends BaseApi {
    getAdditionalInputs(plan: CoursePlanDto): Promise<AdditionalInputsDto> {
        return this.post("additional-inputs", plan);
    }

    generateCourse(plan: CoursePlanDto): Promise<void> {
        return this.post("generate", plan);
    }
}

export default new CourseApi("courses");
