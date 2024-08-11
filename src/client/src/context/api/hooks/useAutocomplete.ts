import { useState } from "react";
import { AutocompleteApi } from "@api";
import { EngineeringDiscipline } from "@models/enums";

export const useAutocomplete = () => {
    const [programmingLanguages, setProgrammingLanguages] = useState<string[]>(
        []
    );
    const [libraries, setLibraries] = useState<string[]>([]);

    return {
        programmingLanguages,
        libraries,
        getProgrammingLanguages: (
            disciplines: EngineeringDiscipline[],
            query: string
        ) => {
            AutocompleteApi.getProgrammingLanguages(disciplines, query).then(
                (languages) => {
                    setProgrammingLanguages(languages);
                }
            );
        },
        getLibraries: (
            subjects: string[],
            languages: string[],
            query: string
        ) => {
            AutocompleteApi.getLibraries(subjects, languages, query).then(
                (libraries) => {
                    setLibraries(libraries);
                }
            );
        },
    };
};
