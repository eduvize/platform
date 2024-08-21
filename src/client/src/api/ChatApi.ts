import { ChatMessagePayload } from "@contracts";
import BaseApi from "./BaseApi";
import { ChatMessageDto, CompletionChunkDto } from "@models/dto";

class ChatApi extends BaseApi {
    sendMessage(
        payload: ChatMessagePayload,
        onData: (chunk: CompletionChunkDto) => void,
        onComplete: () => void
    ) {
        return this.postEventStream("", payload, onData, onComplete);
    }

    getHistory() {
        return this.get<ChatMessageDto[]>("history");
    }
}

export default new ChatApi("chat");
