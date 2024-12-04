import { useEffect, useMemo, useState } from "react";
import {
    PillsInput,
    Group,
    Pill,
    useCombobox,
    Combobox,
    CheckIcon,
} from "@mantine/core";
import { useDebouncedCallback } from "@mantine/hooks";

interface AdvancedPillInputProps {
    valueFetch?: (query: string) => Promise<string[]>;
    defaultValue?: string[];
    value?: string[];
    onChange?: (value: string[]) => void;
    onBlur?: () => void;
    placeholder?: string;
    disabled?: boolean;
    valueSelector?: (value: any) => string;
    valueFilter?: (value: any) => boolean;
    valueMapper?: (value: string) => any;
}

export const AdvancedPillInput = ({
    valueFetch,
    defaultValue,
    value,
    onChange,
    onBlur,
    placeholder,
    valueSelector,
    valueFilter,
    valueMapper,
    disabled,
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

    const handleAutocompletion = useDebouncedCallback((query: string) => {
        if (!valueFetch) return;

        if (query.trim().length === 0) return;

        valueFetch(query).then((options) => {
            setRemoteOptions(options);
        });
    }, 500);

    const handleChange = (newValues: string[]) => {
        console.log("new values", newValues);

        if (onChange) {
            let toChange = newValues;
            let toNotChange: string[] = [];

            if (valueMapper) {
                toChange = toChange.map(valueMapper);
            }

            if (valueFilter) {
                toNotChange = toChange.filter((v) => !valueFilter(v));
                toChange = toChange.filter(valueFilter);
            }

            onChange([...toChange, ...toNotChange]);
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
        if (disabled) {
            combobox.closeDropdown();
            return;
        }

        if (query.length > 0) {
            combobox.openDropdown();
        } else {
            combobox.closeDropdown();
        }
    }, [query, disabled]);

    const handleValueRemove = (val: string) => {
        handleChange(values.filter((v) => v !== val));
    };

    const options = useMemo(
        () =>
            remoteOptions
                .filter((x) =>
                    x.toLocaleLowerCase().includes(query.toLocaleLowerCase())
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
                        {values
                            .filter((x) =>
                                typeof valueFilter !== "undefined"
                                    ? valueFilter(
                                          typeof valueMapper !== "undefined"
                                              ? valueMapper(x)
                                              : x
                                      )
                                    : true
                            )
                            .map((x) => (
                                <Pill
                                    key={x}
                                    size="md"
                                    withRemoveButton
                                    onRemove={() => {
                                        handleValueRemove(x);
                                    }}
                                >
                                    {x}
                                </Pill>
                            ))}

                        <Combobox.DropdownTarget>
                            <Combobox.EventsTarget>
                                <PillsInput.Field
                                    onFocus={() => combobox.openDropdown()}
                                    onBlur={() => {
                                        combobox.closeDropdown();
                                        onBlur?.();
                                    }}
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
                                    disabled={disabled}
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
                    {values
                        .filter((x) =>
                            typeof valueFilter !== "undefined"
                                ? valueFilter(
                                      typeof valueMapper !== "undefined"
                                          ? valueMapper(x)
                                          : x
                                  )
                                : true
                        )
                        .map((x) => (
                            <Pill
                                key={x}
                                size="md"
                                withRemoveButton
                                onRemove={() => {
                                    handleValueRemove(x);
                                }}
                            >
                                {x}
                            </Pill>
                        ))}

                    <PillsInput.Field
                        placeholder={placeholder}
                        onBlur={() => {
                            onBlur?.();
                        }}
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
                        disabled={disabled}
                    />
                </Pill.Group>
            </PillsInput>
        );
    }
};
