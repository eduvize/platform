import { Space, Divider, Text } from "@mantine/core";

interface SpacedDividerProps {
    label?: string;
    labelSize?: "sm" | "md" | "lg" | "xl";
    labelColor?: string;
    labelPosition?: "left" | "center" | "right";
    spacePlacement?: "top" | "bottom" | "top-bottom";
    spacing?: "sm" | "md" | "lg" | "xl";
}

export const SpacedDivider = ({
    label,
    labelSize,
    labelColor,
    labelPosition,
    spacePlacement,
    spacing,
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
                        <Text size={labelSize} c={labelColor}>
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
