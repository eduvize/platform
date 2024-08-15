import { AssertionResult } from "@contracts";
import BaseApi from "./BaseApi";

class ValidationApi extends BaseApi {
    assert(query: string) {
        return this.get<AssertionResult>(`assert?query=${query}`);
    }
}

export default new ValidationApi("validation");
