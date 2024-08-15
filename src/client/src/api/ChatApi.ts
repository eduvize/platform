import { ChatMessagePayload } from "@contracts";
import BaseApi from "./BaseApi";
import { ChatMessageDto } from "@models/dto";

class ChatApi extends BaseApi {
    sendMessage(
        payload: ChatMessagePayload,
        onData: (message: string) => void
    ) {
        return this.postEventStream("", payload, onData);
    }

    getHistory() {
        return this.get<ChatMessageDto[]>("history");
    }
}

export default new ChatApi("chat");
