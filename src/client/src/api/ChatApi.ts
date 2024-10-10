import { ChatMessagePayload } from "@contracts";
import BaseApi from "./BaseApi";
import {
    ChatMessageDto,
    ChatSessionDto,
    CompletionChunkDto,
} from "@models/dto";
import { ChatPromptType } from "@models/enums";

class ChatApi extends BaseApi {
    createSession(
        prompt: ChatPromptType,
        resourceId?: string
    ): Promise<ChatSessionDto> {
        const urlParams = new URLSearchParams();

        urlParams.append("type", prompt);

        if (resourceId) {
            urlParams.append("id", resourceId);
        }

        return this.get<ChatSessionDto>(`session?${urlParams.toString()}`);
    }

    sendMessage(
        sessionId: string,
        payload: ChatMessagePayload,
        onData: (chunk: CompletionChunkDto) => void,
        onComplete: () => void
    ) {
        return this.postEventStream(sessionId, payload, onData, onComplete);
    }

    getHistory(sessionId: string) {
        return this.get<ChatMessageDto[]>(`${sessionId}/history`);
    }
}

export default new ChatApi("chat");
