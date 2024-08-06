import { UserProfileDto } from "./UserProfileDto";

export interface UserDto {
    id: string;
    username: string;
    profile: UserProfileDto;
    created_at_utc: string;
    display_name: string;
}
