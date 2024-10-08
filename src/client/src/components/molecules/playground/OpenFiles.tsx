import { usePlaygroundFilesystem, useReadme } from "@context/playground/hooks";
import { Group, Tabs, Tooltip, Text, ActionIcon } from "@mantine/core";
import Markdown from "react-markdown";
import { FileEditor } from "./FileEditor";
import { useEffect, useRef, useState } from "react";
import { IconX } from "@tabler/icons-react";
import { useResizeObserver } from "@mantine/hooks";

interface OpenFilesProps {
    height: number;
    selectedFile?: string | null;
}

const FileTab = ({
    path,
    onClose,
}: {
    path: string;
    onClose: (path: string) => void;
}) => {
    const fileName = path.split("/").pop();

    return (
        <Tabs.Tab value={path} p="xs">
            <Group align="center" gap="xs">
                <Tooltip label={path} position="bottom">
                    <Text size="sm">{fileName}</Text>
                </Tooltip>
                <ActionIcon
                    size={12}
                    variant="transparent"
                    c="gray"
                    pt={1}
                    onClick={() => onClose(path)}
                >
                    <IconX />
                </ActionIcon>
            </Group>
        </Tabs.Tab>
    );
};

export const OpenFiles = ({
    height,
    selectedFile: overridePath,
}: OpenFilesProps) => {
    const openedRef = useRef<string[]>([]);
    const [tabListRef, tabListRect] = useResizeObserver();
    const readme = useReadme();
    const { openFiles, closeFile, entries } = usePlaygroundFilesystem();
    const [selectedFile, setSelectedFile] = useState<string | null>(
        overridePath || null
    );

    const doesPathExist = (path: string) => {
        const parts = path.split("/");
        let current = entries;

        for (let i = 0; i < parts.length - 1; i++) {
            const part = parts[i];

            const entry = current.find((entry) => entry.name === part);

            if (!entry) {
                return false;
            }

            current = entry.children ?? [];
        }

        return current.some((entry) => entry.name === parts[parts.length - 1]);
    };

    useEffect(() => {
        setSelectedFile(overridePath || "__welcome__");

        if (overridePath) {
            if (!openedRef.current.includes(overridePath)) {
                openedRef.current.push(overridePath);
            }
        }
    }, [overridePath]);

    useEffect(() => {
        // Close files that no longer exist
        const toClose = openFiles.filter((path) => !doesPathExist(path));

        toClose.forEach((path) => closeFile(path));
    }, [entries, openFiles]);

    useEffect(() => {
        // Figure out which file was opened, if any
        const opened = openFiles.filter(
            (path) => !openedRef.current.includes(path)
        );

        if (opened.length) {
            setSelectedFile(opened[0]);
        }

        openedRef.current = [...openFiles];
    }, [openFiles]);

    useEffect(() => {
        if (openedRef.current.length === 0) {
            setSelectedFile("__welcome__");
        }
    }, [openFiles, selectedFile]);

    return (
        <Tabs
            value={selectedFile || "__welcome__"}
            w="100%"
            h="100%"
            onChange={setSelectedFile}
        >
            <Tabs.List ref={tabListRef}>
                <Tabs.Tab value="__welcome__" p="xs">
                    <Text size="sm">README</Text>
                </Tabs.Tab>
                {openFiles.map((path) => (
                    <FileTab key={path} path={path} onClose={closeFile} />
                ))}
            </Tabs.List>

            <Tabs.Panel value="__welcome__">
                {readme || (
                    <Markdown>
                        {`
## Welcome to the Playground
You can create new files and directories using the file explorer on the left, or by using the command line.

In the future, this tab will be replaced with a description of what you'd be working on and the tools provided to you.
`}
                    </Markdown>
                )}
            </Tabs.Panel>

            {openFiles.map((path) => (
                <Tabs.Panel
                    key={path}
                    value={path}
                    mah={`${height - tabListRect.height}px`}
                >
                    <FileEditor
                        path={path}
                        height={height - tabListRect.height}
                    />
                </Tabs.Panel>
            ))}
        </Tabs>
    );
};
