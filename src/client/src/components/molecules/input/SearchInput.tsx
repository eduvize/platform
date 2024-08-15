import { useEffect, useState } from "react";
import { Autocomplete, AutocompleteProps } from "@mantine/core";
import { useDebouncedCallback } from "@mantine/hooks";

interface SearchInputProps extends AutocompleteProps {
    valueFetch: (query: string) => Promise<string[]>;
    onChange?: (value: string) => void;
    value?: string;
}

export const SearchInput = (props: SearchInputProps) => {
    const { valueFetch } = props;
    const [value, setValue] = useState(props.value || "");
    const [results, setResults] = useState<string[]>([]);

    const handleFetchResults = useDebouncedCallback((query: string) => {
        valueFetch(query).then((data) => {
            setResults(data);
        });
    }, 500);

    useEffect(() => {
        if (props.onChange) {
            props.onChange(value);
        }
    }, [value]);

    return (
        <Autocomplete
            {...props}
            data={results}
            onChange={(val) => handleFetchResults(val)}
            onOptionSubmit={(val) => setValue(val)}
        />
    );
};
