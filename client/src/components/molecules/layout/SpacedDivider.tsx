import { Space, Divider, Text } from "@mantine/core";

interface SpacedDividerProps {
    label?: string;
    labelSize?: "sm" | "md" | "lg" | "xl";
    labelColor?: string;
    labelPosition?: "left" | "center" | "right";
    spacePlacement?: "top" | "bottom" | "top-bottom";
    spacing?: "sm" | "md" | "lg" | "xl";
    bold?: boolean;
}

export const SpacedDivider = ({
    label,
    labelSize,
    labelColor,
    labelPosition,
    spacePlacement,
    spacing,
    bold,
}: SpacedDividerProps) => {
    return (
        <>
            {(spacePlacement === "top" ||
                spacePlacement === "top-bottom" ||
                !spacePlacement) && <Space h={spacing} />}
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
            {(spacePlacement === "bottom" ||
                spacePlacement === "top-bottom" ||
                !spacePlacement) && <Space h={spacing} />}
        </>
    );
};
