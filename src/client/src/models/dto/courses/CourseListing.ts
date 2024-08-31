export interface CourseListingDto {
    id: string;
    title: string;
    description: string;
    cover_image_url: string;
    is_generating: boolean;
    generation_progress: number;
}
