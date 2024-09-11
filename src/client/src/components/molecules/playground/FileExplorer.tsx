import { Group, Tree, Text } from "@mantine/core";
import { IconChevronDown } from "@tabler/icons-react";

interface FileExplorerProps {
    w?: number | string;
}

export const FileExplorer = ({ w }: FileExplorerProps) => {
    const data = [
        {
            label: "src",
            value: "/src",
            children: [
                {
                    label: "app",
                    value: "/src/app",
                    children: [
                        {
                            label: "main.py",
                            value: "/src/app/main.py",
                        },
                        {
                            label: "config.py",
                            value: "/src/app/config.py",
                        },
                    ],
                },
                {
                    label: "run.py",
                    value: "/src/run.py",
                },
            ],
        },
    ];

    return (
        <Tree
            w={w}
            p="xs"
            data={data}
            levelOffset={23}
            selectOnClick
            renderNode={({ node, expanded, hasChildren, elementProps }) => (
                <Group gap={5} {...elementProps}>
                    {hasChildren && (
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
                        {node.label}
                    </Text>
                </Group>
            )}
        />
    );
};
