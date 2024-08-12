import { ChatSessionDto } from "@models/dto";

export interface ChatMessagePayload extends ChatSessionDto {
    message: string;
}
