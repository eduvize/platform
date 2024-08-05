import { EngineeringDiscipline } from "../models/enums";
import BaseApi from "./BaseApi";

class AutocompleteApi extends BaseApi {
    getProgrammingLanguages(query: string): Promise<string[]> {
        return this.get<string[]>(
            `programming-languages?query=${encodeURIComponent(query)}`
        );
    }

    getLibraries(
        subjects: EngineeringDiscipline[],
        query: string
    ): Promise<string[]> {
        return this.get<string[]>(
            `libraries?subjects=${subjects.join(
                ","
            )}&query=${encodeURIComponent(query)}`
        );
    }
}

export default new AutocompleteApi("autocomplete");
