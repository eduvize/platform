import { UserProfileDto } from "../../models/dto/profile";

export interface ProfileUpdatePayload
    extends Omit<UserProfileDto, "avatar_url"> {
    avatar_file_id?: string;
}
