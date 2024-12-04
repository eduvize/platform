import { ModuleDto } from "./Module";

export interface CourseDto {
    id: string;
    title: string;
    description: string;
    cover_image_url: string;
    current_lesson_id: string;
    current_section_index: number;
    created_at_utc: string;
    completed_at_utc?: string;

    modules: ModuleDto[];
}
