import { PlaygroundCreationResponse } from "@contracts";
import BaseApi from "./BaseApi";

class PlaygroundApi extends BaseApi {
    createSession(): Promise<PlaygroundCreationResponse> {
        return this.post("", {});
    }
}

export default new PlaygroundApi("playground");
