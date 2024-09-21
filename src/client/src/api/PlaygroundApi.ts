import { PlaygroundCreationResponse } from "@contracts";
import BaseApi from "./BaseApi";

class PlaygroundApi extends BaseApi {
    createSession(environmentId: string): Promise<PlaygroundCreationResponse> {
        return this.get(environmentId);
    }
}

export default new PlaygroundApi("playground");
