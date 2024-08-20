import { Group, Loader, Text } from "@mantine/core";

interface PendingToolProps {
    name: string;
}

export const PendingTool = ({ name }: PendingToolProps) => {
    return (
        <Group pl="lg">
            <Loader type="oval" size="sm" />

            <Text size="sm">{name}</Text>
        </Group>
    );
};
