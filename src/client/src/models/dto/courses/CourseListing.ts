export interface CourseListingDto {
    id: string;
    title: string;
    description: string;
    cover_image_url: string;
    progress: number;
    is_generating: boolean;
    generation_progress: number;
}
