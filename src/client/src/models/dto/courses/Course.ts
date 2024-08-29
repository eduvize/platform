import { ModuleDto } from "./Module";

export interface CourseDto {
    title: string;
    description: string;
    cover_image_url: string;

    modules: ModuleDto[];
}
