import { ChatMessagePayload, CreateSessionResponse } from "@contracts";
import BaseApi from "./BaseApi";
import { ChatMessageDto, CompletionChunkDto } from "@models/dto";
import { ChatPromptType } from "@models/enums";

class ChatApi extends BaseApi {
    createSession(
        prompt: ChatPromptType,
        resourceId?: string
    ): Promise<CreateSessionResponse> {
        const urlParams = new URLSearchParams();

        urlParams.append("type", prompt);

        if (resourceId) {
            urlParams.append("id", resourceId);
        }

        return this.get<CreateSessionResponse>(
            `session?${urlParams.toString()}`
        );
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
