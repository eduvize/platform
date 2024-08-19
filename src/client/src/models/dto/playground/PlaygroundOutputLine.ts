export type OutputType = "input" | "output" | "error";

export interface PlaygroundOutputLine {
    text: string;
    type: OutputType;
}
