export interface FilesystemEntry {
    name: string;
    path: string;
    type: "file" | "directory";
    children?: FilesystemEntry[];
}

export interface PlaygroundEnvironment {
    filesystem: FilesystemEntry[];
}
