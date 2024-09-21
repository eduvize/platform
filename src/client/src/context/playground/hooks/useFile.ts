import { useDebouncedCallback } from "@mantine/hooks";
import { useEffect, useState } from "react";
import { useContextSelector } from "use-context-selector";
import { PlaygroundContext } from "../PlaygroundContext";

interface UseFileReturn {
    isLoaded: boolean;
    content: string;
    setContent: (content: string) => void;
}

export const useFile = (path: string): UseFileReturn => {
    const openFiles = useContextSelector(PlaygroundContext, (v) => v.openFiles);
    const setRemoteContent = useContextSelector(
        PlaygroundContext,
        (v) => v.setFileContent
    );
    const [content, setContent] = useState<string | null>(null);

    const remoteFile = openFiles[path];

    useEffect(() => {
        if (remoteFile) {
            setContent(remoteFile);
        }
    }, [remoteFile]);

    const updateRemoteContent = useDebouncedCallback(() => {
        if (!content) return;

        setRemoteContent(path, content);
    }, 1000);

    useEffect(() => {
        if (content) {
            updateRemoteContent();
        }
    }, [content]);

    return {
        isLoaded: !!content,
        content: content ?? "",
        setContent,
    };
};
