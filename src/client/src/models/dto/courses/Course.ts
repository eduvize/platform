import { ModuleDto } from "./Module";

export interface CourseDto {
    title: string;
    description: string;

    modules: ModuleDto[];
}
