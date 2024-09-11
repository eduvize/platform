import { useContextSelector } from "use-context-selector";
import { PlaygroundContext } from "../PlaygroundContext";
import { FilesystemEntry } from "@models/dto";

interface UsePlaygroundFilesystemReturn {
    entries: FilesystemEntry[];
    createFile: (path: string) => void;
    createDirectory: (path: string) => void;
}

export const usePlaygroundFilesystem = (): UsePlaygroundFilesystemReturn => {
    const create = useContextSelector(PlaygroundContext, (v) => v.create);
    const entries =
        useContextSelector(
            PlaygroundContext,
            (v) => v.environment?.filesystem
        ) ?? [];

    return {
        entries,
        createFile: (path: string) => create("file", path),
        createDirectory: (path: string) => create("directory", path),
    };
};
