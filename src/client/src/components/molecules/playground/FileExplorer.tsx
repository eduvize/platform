import { usePlaygroundFilesystem } from "@context/playground/hooks";
import {
    Group,
    Tree,
    Text,
    useTree,
    Stack,
    Input,
    TreeNodeData,
} from "@mantine/core";
import { FilesystemEntry } from "@models/dto";
import { IconChevronDown } from "@tabler/icons-react";
import { useContextMenu } from "mantine-contextmenu";
import { useEffect, useMemo, useState } from "react";

interface FileExplorerProps {
    w?: number | string;
    onSelect?: (type: "file" | "directory", path: string) => void;
}

interface EntryData {
    type: "file" | "directory";
    name: string;
    dir: string;
}

interface RenameData extends EntryData {
    newName: string;
}

export const FileExplorer = ({ w, onSelect }: FileExplorerProps) => {
    const tree = useTree();
    const { showContextMenu } = useContextMenu();
    const {
        entries,
        createDirectory,
        createFile,
        openFile,
        rename,
        deletePath,
        openFiles,
    } = usePlaygroundFilesystem();
    const [newEntry, setNewEntry] = useState<EntryData | null>(null);
    const [renameEntry, setRenameEntry] = useState<RenameData | null>(null);

    useEffect(() => {
        tree.clearSelected();

        for (const path of openFiles) {
            tree.select(path);
        }
    }, [openFiles.length]);

    const handleAddFile = (dir: string) => {
        tree.expand(dir);

        setNewEntry({
            type: "file",
            dir,
            name: "",
        });
    };

    const handleAddDirectory = (dir: string) => {
        tree.expand(dir);

        setNewEntry({
            type: "directory",
            dir,
            name: "",
        });
    };

    const handleNewEntrySubmit = () => {
        if (!newEntry) return;

        if (newEntry.name !== "") {
            if (newEntry.type === "file") {
                createFile(`${newEntry.dir}/${newEntry.name}`);
            } else {
                createDirectory(`${newEntry.dir}/${newEntry.name}`);
            }
        }

        setNewEntry(null);
    };

    const getEntryFromNestedEntries = (path: string) => {
        const parts = path.split("/");
        let current = entries;

        for (let i = 0; i < parts.length - 1; i++) {
            const part = parts[i];

            const entry = current.find((entry) => entry.name === part);

            if (!entry) {
                return null;
            }

            current = entry.children ?? [];
            console.log(part);
            console.log(current);
        }

        return current.find((entry) => entry.name === parts[parts.length - 1]);
    };

    const handleRename = (type: "file" | "directory", path: string) => {
        if (renameEntry) return;

        const entry = getEntryFromNestedEntries(path);
        const dirName = path.split("/").slice(0, -1).join("/");

        setRenameEntry({
            type,
            dir: dirName,
            name: entry?.name ?? "",
            newName: entry?.name ?? "",
        });
    };

    const handleRenameSubmit = () => {
        if (!renameEntry || renameEntry.name.trim().length === 0) return;

        rename(
            `${renameEntry.dir}/${renameEntry.name}`,
            `${renameEntry.dir}/${renameEntry.newName}`
        );
        setRenameEntry(null);
    };

    const getContextMenu = (entry: TreeNodeData) => {
        if (`${entry.label}` === "__new__") return;

        if (`${entry.label}`.startsWith("file:")) {
            return showContextMenu(
                [
                    {
                        key: "rename-file",
                        title: "Rename...",
                        onClick: () => handleRename("file", entry.value),
                    },
                    {
                        key: "delete-file",
                        title: "Delete",
                        onClick: () => deletePath(entry.value),
                    },
                ],
                {
                    style: {
                        padding: "8px",
                    },
                }
            );
        } else {
            return showContextMenu(
                [
                    {
                        key: "new-file",
                        title: "New File",
                        onClick: () => handleAddFile(entry.value),
                    },
                    {
                        key: "new-directory",
                        title: "New Directory",
                        onClick: () => handleAddDirectory(entry.value),
                    },
                    {
                        key: "rename-directory",
                        title: "Rename...",
                        onClick: () => handleRename("directory", entry.value),
                    },
                    {
                        key: "delete-directory",
                        title: "Delete",
                        onClick: () => deletePath(entry.value),
                    },
                ],
                {
                    style: {
                        padding: "8px",
                    },
                }
            );
        }
    };

    const data = useMemo(() => {
        function makeEntry(entry: FilesystemEntry): any {
            if (
                renameEntry &&
                entry.path === `${renameEntry.dir}/${renameEntry.name}`
            ) {
                return {
                    label: "__rename__",
                    value: "__rename__",
                };
            }

            if (entry.type === "directory") {
                let children = entry.children?.map(makeEntry) ?? [];

                // Filter out any rename/new entries that are already in the directory
                children = children.filter(
                    (child) => !(renameEntry && renameEntry.dir === child.path)
                );

                if (newEntry && newEntry.dir === entry.path) {
                    children = [
                        ...children,
                        {
                            label: "__new__",
                            value: "__new__",
                        },
                    ];
                }

                return {
                    label: `dir:${entry.name}`,
                    value: entry.path,
                    children,
                };
            } else {
                return {
                    label: `file:${entry.name}`,
                    value: entry.path,
                };
            }
        }

        let list = entries.map(makeEntry);

        if (newEntry && newEntry.dir === "/") {
            list = [
                ...list,
                {
                    label: "__new__",
                    value: "__new__",
                },
            ];
        }

        return list;
    }, [entries, newEntry, renameEntry]);

    return (
        <Stack gap="xs" h="100%">
            <Text
                size="xs"
                tt="uppercase"
                fw={500}
                c="gray"
                bg="dark"
                p="xs"
                pb={0}
            >
                File Explorer
            </Text>

            <Tree
                w={w}
                h="100%"
                tree={tree}
                data={data}
                selectOnClick
                expandOnClick
                renderNode={({ node, expanded, elementProps }) =>
                    node.label === "__new__" ? (
                        <Input
                            size="xs"
                            px="xs"
                            autoFocus
                            value={newEntry?.name || ""}
                            onChange={(evt) =>
                                setNewEntry((prev) => ({
                                    ...prev!,
                                    name: evt.target.value,
                                }))
                            }
                            onKeyDown={(evt) => {
                                if (evt.key === "Enter") {
                                    handleNewEntrySubmit();
                                }
                            }}
                            onBlur={handleNewEntrySubmit}
                        />
                    ) : node.label === "__rename__" ? (
                        <Input
                            size="xs"
                            px="xs"
                            autoFocus
                            value={renameEntry?.newName || ""}
                            onChange={(evt) =>
                                setRenameEntry((prev) => ({
                                    ...prev!,
                                    newName: evt.target.value,
                                }))
                            }
                            onKeyDown={(evt) => {
                                if (evt.key === "Enter") {
                                    handleRenameSubmit();
                                }
                            }}
                            onFocus={(evt) => evt.target.select()}
                            onBlur={handleRenameSubmit}
                        />
                    ) : (
                        <Group
                            gap={5}
                            {...elementProps}
                            onClick={() => {
                                if (node.label === "__new__") return;

                                tree.select(node.value);

                                if (onSelect) {
                                    onSelect(
                                        `${node.label}`.startsWith("dir:")
                                            ? "directory"
                                            : "file",
                                        node.value
                                    );
                                }

                                if (`${node.label}`.startsWith("dir:")) {
                                    tree.toggleExpanded(node.value);
                                    return;
                                } else {
                                    openFile(node.value);
                                }
                            }}
                            onContextMenu={getContextMenu(node)}
                        >
                            {`${node.label}`.startsWith("dir:") && (
                                <IconChevronDown
                                    size={12}
                                    style={{
                                        transform: expanded
                                            ? "rotate(0deg)"
                                            : "rotate(270deg)",
                                    }}
                                />
                            )}

                            <Text c="gray" size="sm">
                                {`${node.label}`.split(":")[1]}
                            </Text>
                        </Group>
                    )
                }
                onContextMenu={showContextMenu(
                    [
                        {
                            key: "new-file",
                            title: "New File",
                            onClick: () => handleAddFile("/"),
                        },
                        {
                            key: "new-directory",
                            title: "New Directory",
                            onClick: () => handleAddDirectory("/"),
                        },
                    ],
                    {
                        style: {
                            padding: "8px",
                        },
                    }
                )}
            />
        </Stack>
    );
};
