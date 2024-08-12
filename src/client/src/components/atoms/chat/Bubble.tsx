import { ReactNode } from "react";
import { Box, BoxProps, DefaultMantineColor } from "@mantine/core";
import { useMantineTheme } from "@mantine/core";

interface BubbleProps extends BoxProps {
    tipSide: "left" | "right";
    children: ReactNode;
}

export const Bubble = (props: BubbleProps) => {
    const { tipSide } = props;

    function getColorVariable(
        colorName: DefaultMantineColor,
        shade: number = 8
    ) {
        const theme = useMantineTheme();
        const color = theme.colors[colorName];

        if (!color) {
            throw new Error(
                `Color "${colorName}" does not exist in the theme.`
            );
        }

        return color[shade]; // Returns the color variable for the given shade
    }

    return (
        <Box
            {...props}
            component="span"
            p="xs"
            style={{
                borderRadius: "var(--mantine-radius-lg)",
                position: "relative",
                display: "inline-block",
                wordBreak: "break-word",
            }}
        >
            {tipSide === "left" && (
                <div
                    style={{
                        position: "absolute",
                        top: "50%",
                        left: "-18px",
                        transform: "translateY(-50%)",
                        width: 0,
                        height: 0,
                        borderLeft: "10px solid transparent",
                        borderRight: `10px solid ${getColorVariable(
                            props.bg as DefaultMantineColor
                        )}`,
                        borderTop: "10px solid transparent",
                        borderBottom: "10px solid transparent",
                    }}
                />
            )}
            {tipSide === "right" && (
                <div
                    style={{
                        position: "absolute",
                        top: "50%",
                        right: "-18px",
                        transform: "translateY(-50%)",
                        width: 0,
                        height: 0,
                        borderLeft: `10px solid ${getColorVariable(
                            props.bg as DefaultMantineColor
                        )}`,
                        borderRight: "10px solid transparent",
                        borderTop: "10px solid transparent",
                        borderBottom: "10px solid transparent",
                    }}
                />
            )}
            {props.children}
        </Box>
    );
};
