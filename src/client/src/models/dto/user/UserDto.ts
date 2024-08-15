import { UserProfileDto } from "@models/dto";

export interface UserDto {
    id: string;
    username: string;
    profile: UserProfileDto;
    created_at_utc: string;
    display_name: string;
}
