import { useNavigate } from "react-router-dom";
import { ReactNode } from "react";
import { Box, Button, Card, Group, Space, Text } from "@mantine/core";
import classes from "./Banner.module.css";

interface BannerAction {
    label: string;
    onClick?: () => void;
    href?: string;
}

interface BannerProps {
    icon?: ReactNode;
    title: string;
    description: string;
    actions?: BannerAction[];
    variant?: "danger" | "warning" | "info";
}

export const Banner = ({
    icon,
    title,
    description,
    variant,
    actions,
}: BannerProps) => {
    const navigate = useNavigate();

    const lines = description.split("\n");

    return (
        <Card
            withBorder
            className={`${classes.card} ${classes[variant || "default"]}`}
        >
            <Group wrap="nowrap">
                {icon && (
                    <Box
                        className={`${classes.icon} ${
                            classes[variant || "default"]
                        }`}
                        mr="xs"
                        style={{ zoom: 2 }}
                    >
                        {icon}
                    </Box>
                )}

                <Box>
                    <Text size="md" fw={700}>
                        {title}
                    </Text>

                    {lines.map((line) =>
                        line.length === 0 ? (
                            <Space h="sm" />
                        ) : (
                            <Text fw={400} size="sm">
                                {line}
                            </Text>
                        )
                    )}

                    {actions && (
                        <Group justify="flex-end" mt="sm">
                            {actions.map((action) => (
                                <Button
                                    variant="outline"
                                    className={`${classes.button} ${
                                        classes[variant || "default"]
                                    }`}
                                    size="compact-sm"
                                    onClick={() => {
                                        if (action.href) {
                                            navigate(action.href);
                                        }

                                        if (action.onClick) {
                                            action.onClick();
                                        }
                                    }}
                                >
                                    {action.label}
                                </Button>
                            ))}
                        </Group>
                    )}
                </Box>
            </Group>
        </Card>
    );
};
