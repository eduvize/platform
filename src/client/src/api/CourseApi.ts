import BaseApi from "./BaseApi";
import {
    AdditionalInputsDto,
    CourseDto,
    CourseListingDto,
    CoursePlan as CoursePlanDto,
    CourseProgressionDto,
} from "@models/dto";

class CourseApi extends BaseApi {
    getAdditionalInputs(plan: CoursePlanDto): Promise<AdditionalInputsDto> {
        return this.post("additional-inputs", plan);
    }

    generateCourse(plan: CoursePlanDto): Promise<void> {
        return this.post("generate", plan);
    }

    markLessonComplete(
        courseId: string,
        lessonId: string
    ): Promise<CourseProgressionDto> {
        return this.post(`${courseId}/lesson/${lessonId}/complete`, {});
    }

    getCourses(): Promise<CourseListingDto[]> {
        return this.get("");
    }

    getCourse(id: string): Promise<CourseDto> {
        return this.get(id);
    }
}

export default new CourseApi("courses");
