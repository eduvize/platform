import { useContextSelector } from "use-context-selector";
import { PlaygroundContext } from "../PlaygroundContext";
import { FilesystemEntry } from "@models/dto";

interface UsePlaygroundFilesystemReturn {
    entries: FilesystemEntry[];
    openFiles: string[];
    openFile: (path: string) => void;
    closeFile: (path: string) => void;
    createFile: (path: string) => void;
    createDirectory: (path: string) => void;
}

export const usePlaygroundFilesystem = (): UsePlaygroundFilesystemReturn => {
    const create = useContextSelector(PlaygroundContext, (v) => v.create);
    const openFile = useContextSelector(PlaygroundContext, (v) => v.openFile);
    const closeFile = useContextSelector(PlaygroundContext, (v) => v.closeFile);
    const openFiles = useContextSelector(PlaygroundContext, (v) => v.openFiles);
    const entries =
        useContextSelector(
            PlaygroundContext,
            (v) => v.environment?.filesystem
        ) ?? [];

    return {
        entries,
        openFiles: Object.keys(openFiles),
        openFile,
        closeFile,
        createFile: (path: string) => create("file", path),
        createDirectory: (path: string) => create("directory", path),
    };
};
