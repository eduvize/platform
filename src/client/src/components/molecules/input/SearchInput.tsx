import { Autocomplete, AutocompleteProps } from "@mantine/core";
import { useThrottledCallback } from "@mantine/hooks";
import { useEffect, useState } from "react";

interface SearchInputProps extends AutocompleteProps {
    valueFetch: (query: string) => Promise<string[]>;
    onChange?: (value: string) => void;
}

export const SearchInput = (props: SearchInputProps) => {
    const { valueFetch } = props;
    const [value, setValue] = useState("");
    const [results, setResults] = useState<string[]>([]);

    const handleFetchResults = useThrottledCallback((query: string) => {
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
