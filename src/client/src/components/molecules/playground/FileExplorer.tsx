import { usePlaygroundFilesystem } from "@context/playground/hooks";
import { Group, Tree, Text, useTree } from "@mantine/core";
import { FilesystemEntry } from "@models/dto";
import { IconChevronDown } from "@tabler/icons-react";
import { useEffect, useMemo } from "react";

interface FileExplorerProps {
    w?: number | string;
}

export const FileExplorer = ({ w }: FileExplorerProps) => {
    const tree = useTree();
    const { entries, createDirectory, createFile, openFile, openFiles } =
        usePlaygroundFilesystem();

    useEffect(() => {
        tree.clearSelected();

        for (const path of openFiles) {
            tree.select(path);
        }
    }, [openFiles]);

    const data = useMemo(() => {
        function makeDirectoryEntry(entry: FilesystemEntry): any {
            return {
                label: `dir:${entry.name}`,
                value: entry.path,
                children: entry.children?.map(makeDirectoryEntry) ?? [],
            };
        }

        return entries.map((entry) => {
            if (entry.type === "directory") {
                return makeDirectoryEntry(entry);
            }

            return {
                label: `file:${entry.name}`,
                value: entry.path,
            };
        });
    }, [entries]);

    return (
        <Tree
            w={w}
            p="xs"
            data={data}
            levelOffset={23}
            selectOnClick
            renderNode={({ node, expanded, hasChildren, elementProps }) => (
                <Group
                    gap={5}
                    {...elementProps}
                    onClick={(evt) => {
                        elementProps.onClick?.(evt);

                        if (`${node.label}`.startsWith("dir:")) {
                            tree.toggleExpanded(node.value);
                            return;
                        }

                        openFile(node.value);
                    }}
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
            )}
        />
    );
};
