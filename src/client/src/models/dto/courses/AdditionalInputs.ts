export type AdditionalInputType = "text" | "select" | "multiselect";

export interface AdditionalInputDto {
    required: boolean;
    name: string;
    short_label: string;
    description?: string;
    input_type: AdditionalInputType;
    depends_on_input_name?: string;
    depends_on_input_value?: string;
    options?: string[];
}

export interface AdditionalInputsDto {
    inputs: AdditionalInputDto[];
}
