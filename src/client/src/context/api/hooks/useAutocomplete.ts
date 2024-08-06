import { useState } from "react";
import { EngineeringDiscipline } from "../../../models/enums";
import AutocompleteApi from "../../../api/AutocompleteApi";

export const useAutocomplete = () => {
    const [programmingLanguages, setProgrammingLanguages] = useState<string[]>(
        []
    );
    const [libraries, setLibraries] = useState<string[]>([]);

    return {
        programmingLanguages,
        libraries,
        getProgrammingLanguages: (query: string) => {
            AutocompleteApi.getProgrammingLanguages(query).then((languages) => {
                setProgrammingLanguages(languages);
            });
        },
        getLibraries: (subjects: EngineeringDiscipline[], query: string) => {
            AutocompleteApi.getLibraries(subjects, query).then((libraries) => {
                setLibraries(libraries);
            });
        },
    };
};
