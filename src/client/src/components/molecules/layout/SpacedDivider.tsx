import {
    Space,
    Divider,
    Text,
    Group,
    Grid,
    Center,
    Stack,
} from "@mantine/core";
import { IconCirclePlusFilled } from "@tabler/icons-react";

interface SpacedDividerProps {
    label?: string;
    labelSize?: "sm" | "md" | "lg" | "xl";
    labelColor?: string;
    labelPosition?: "left" | "center" | "right";
    spacePlacement?: "top" | "bottom" | "top-bottom";
    spacing?: "sm" | "md" | "lg" | "xl";
    bold?: boolean;
    icon?: React.ReactNode;
}

export const SpacedDivider = ({
    label,
    labelSize,
    labelColor,
    labelPosition,
    spacePlacement,
    spacing,
    bold,
    icon,
}: SpacedDividerProps) => {
    return (
        <>
            {(spacePlacement === "top" ||
                spacePlacement === "top-bottom" ||
                !spacePlacement) && <Space h={spacing} />}
            <Grid>
                <Grid.Col span={!!icon ? 11 : 12}>
                    <Divider
                        labelPosition={labelPosition}
                        label={
                            label ? (
                                <Text
                                    size={labelSize}
                                    c={labelColor}
                                    fw={bold ? "bold" : undefined}
                                >
                                    {label}
                                </Text>
                            ) : undefined
                        }
                        size="sm"
                    />
                </Grid.Col>

                {!!icon && (
                    <Grid.Col span={1}>
                        <Center mt="0.1em">{icon}</Center>
                    </Grid.Col>
                )}
            </Grid>
            {(spacePlacement === "bottom" ||
                spacePlacement === "top-bottom" ||
                !spacePlacement) && <Space h={spacing} />}
        </>
    );
};
