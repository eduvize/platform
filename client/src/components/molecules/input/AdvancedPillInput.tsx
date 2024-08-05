import {
    PillsInput,
    Group,
    Pill,
    useCombobox,
    Combobox,
    CheckIcon,
} from "@mantine/core";
import { useThrottledCallback } from "@mantine/hooks";
import { useEffect, useMemo, useState } from "react";

interface AdvancedPillInputProps {
    valueFetch?: (query: string) => Promise<string[]>;
    defaultValue?: string[];
    value?: string[];
    onChange?: (value: string[]) => void;
    placeholder?: string;
    valueSelector?: (value: any) => string;
    valueMapper?: (value: string) => any;
}

export const AdvancedPillInput = ({
    valueFetch,
    defaultValue,
    value,
    onChange,
    placeholder,
    valueSelector,
    valueMapper,
}: AdvancedPillInputProps) => {
    function mapValues(elements: any[]) {
        if (!valueSelector) {
            return elements;
        }

        return elements.map((element) => {
            if (typeof element === "string") {
                return element;
            }

            return valueSelector(element);
        });
    }

    const [remoteOptions, setRemoteOptions] = useState<string[]>([]);
    const [query, setQuery] = useState("");
    const combobox = useCombobox({
        onDropdownClose: () => combobox.resetSelectedOption(),
        onDropdownOpen: () => combobox.updateSelectedOptionIndex("active"),
    });

    const initialValue = defaultValue || value || [];
    const values = mapValues(initialValue);

    const handleAutocompletion = useThrottledCallback((query: string) => {
        if (!valueFetch) return;

        if (query.trim().length === 0) return;

        valueFetch(query).then((options) => {
            setRemoteOptions(options);
        });
    }, 300);

    const handleChange = (newValues: string[]) => {
        if (onChange) {
            if (valueMapper) {
                onChange(newValues.map(valueMapper));
            } else {
                onChange(newValues);
            }
        }
    };

    useEffect(() => {
        if (!valueFetch) return;

        if (query.trim().length === 0) {
            setRemoteOptions([]);

            return;
        }

        handleAutocompletion(query);
    }, [valueFetch, query]);

    useEffect(() => {
        if (query.length > 0) {
            combobox.openDropdown();
        } else {
            combobox.closeDropdown();
        }
    }, [query]);

    const handleValueRemove = (val: string) => {
        handleChange(values.filter((v) => v !== val));
    };

    const options = useMemo(
        () =>
            remoteOptions
                .filter((item) =>
                    item.toLowerCase().includes(query.trim().toLowerCase())
                )
                .map((item) => (
                    <Combobox.Option
                        key={item}
                        value={item}
                        active={value?.includes(item)}
                    >
                        <Group gap="sm">
                            {value?.includes(item) ? (
                                <CheckIcon size={12} />
                            ) : null}
                            <span>{item}</span>
                        </Group>
                    </Combobox.Option>
                )),
        [remoteOptions]
    );

    if (valueFetch) {
        return (
            <Combobox
                store={combobox}
                onOptionSubmit={(val) => {
                    handleChange([...values, val]);
                    setQuery("");
                }}
            >
                <PillsInput>
                    <Pill.Group>
                        {values.map((lang) => (
                            <Pill
                                key={lang}
                                size="md"
                                withRemoveButton
                                onRemove={() => {
                                    handleValueRemove(lang);
                                }}
                            >
                                {lang}
                            </Pill>
                        ))}

                        <Combobox.DropdownTarget>
                            <Combobox.EventsTarget>
                                <PillsInput.Field
                                    onFocus={() => combobox.openDropdown()}
                                    onBlur={() => combobox.closeDropdown()}
                                    placeholder={placeholder}
                                    value={query}
                                    onChange={(event) => {
                                        combobox.updateSelectedOptionIndex();
                                        setQuery(event.currentTarget.value);
                                    }}
                                    onKeyDown={(event) => {
                                        if (
                                            event.key === "Backspace" &&
                                            query.length === 0
                                        ) {
                                            event.preventDefault();
                                            if (value) {
                                                handleValueRemove(
                                                    value[value.length - 1]
                                                );
                                            }
                                        }
                                    }}
                                />
                            </Combobox.EventsTarget>
                        </Combobox.DropdownTarget>
                    </Pill.Group>
                </PillsInput>

                <Combobox.Dropdown>
                    <Combobox.Options>
                        {options.length > 0 ? (
                            options
                        ) : (
                            <Combobox.Empty>No options found</Combobox.Empty>
                        )}
                    </Combobox.Options>
                </Combobox.Dropdown>
            </Combobox>
        );
    } else {
        return (
            <PillsInput>
                <Pill.Group>
                    {values.map((lang) => (
                        <Pill
                            key={lang}
                            size="md"
                            withRemoveButton
                            onRemove={() => {
                                handleValueRemove(lang);
                            }}
                        >
                            {lang}
                        </Pill>
                    ))}

                    <PillsInput.Field
                        placeholder={placeholder}
                        onKeyDown={(event) => {
                            if (event.key === "Enter") {
                                event.preventDefault();
                                handleChange([
                                    ...values,
                                    event.currentTarget.value,
                                ]);
                                event.currentTarget.value = "";
                            }
                        }}
                    />
                </Pill.Group>
            </PillsInput>
        );
    }
};
