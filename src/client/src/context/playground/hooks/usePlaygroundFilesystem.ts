import { useContextSelector } from "use-context-selector";
import { PlaygroundContext } from "../PlaygroundContext";
import { FilesystemEntry } from "@models/dto";

interface UsePlaygroundFilesystemReturn {
    entries: FilesystemEntry[];
    openFiles: string[];
    openFile: (path: string) => void;
    closeFile: (path: string) => void;
    createFile: (path: string) => void;
    rename: (path: string, newPath: string) => void;
    deletePath: (path: string) => void;
    createDirectory: (path: string) => void;
    expandPath: (path: string) => void;
    collapsePath: (path: string) => void;
}

export const usePlaygroundFilesystem = (): UsePlaygroundFilesystemReturn => {
    const create = useContextSelector(PlaygroundContext, (v) => v.create);
    const rename = useContextSelector(PlaygroundContext, (v) => v.rename);
    const deletePath = useContextSelector(
        PlaygroundContext,
        (v) => v.deletePath
    );
    const openFile = useContextSelector(PlaygroundContext, (v) => v.openFile);
    const closeFile = useContextSelector(PlaygroundContext, (v) => v.closeFile);
    const openFiles = useContextSelector(PlaygroundContext, (v) => v.openFiles);
    const expandPath = useContextSelector(
        PlaygroundContext,
        (v) => v.expandPath
    );
    const collapsePath = useContextSelector(
        PlaygroundContext,
        (v) => v.collapsePath
    );
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
        rename,
        deletePath,
        createDirectory: (path: string) => create("directory", path),
        expandPath,
        collapsePath,
    };
};
