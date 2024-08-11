import BaseApi from "./BaseApi";
import { EngineeringDiscipline } from "@models/enums";

class AutocompleteApi extends BaseApi {
    getProgrammingLanguages(
        disciplines: EngineeringDiscipline[],
        query: string
    ): Promise<string[]> {
        const params = {
            disciplines: disciplines
                .map((d) => EngineeringDiscipline[d])
                .join(","),
            query: encodeURIComponent(query),
        };

        return this.get<string[]>(
            `programming-languages?${new URLSearchParams(params).toString()}`
        );
    }

    getLibraries(
        subjects: string[],
        languages: string[],
        query: string
    ): Promise<string[]> {
        const params = {
            subjects: subjects.join(","),
            languages: languages.join(","),
            query: encodeURIComponent(query),
        };

        return this.get<string[]>(
            `libraries?${new URLSearchParams(params).toString()}`
        );
    }

    getEducationalInstitutions(query: string): Promise<string[]> {
        return this.get<string[]>(
            `educational-institutions?query=${encodeURIComponent(query)}`
        );
    }

    getEducationalFocuses(
        schoolName: string,
        query: string
    ): Promise<string[]> {
        return this.get<string[]>(
            `educational-focuses?school_name=${encodeURIComponent(
                schoolName
            )}&query=${encodeURIComponent(query)}`
        );
    }
}

export default new AutocompleteApi("autocomplete");
