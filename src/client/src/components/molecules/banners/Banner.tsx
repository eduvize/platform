import { useNavigate } from "react-router-dom";
import { ReactNode, useEffect, useState } from "react";
import {
    Box,
    Button,
    Card,
    Container,
    Group,
    Space,
    Text,
} from "@mantine/core";
import classes from "./Banner.module.css";

interface BannerAction {
    label: string;
    onClick?: () => void;
    href?: string;
    dismiss?: boolean;
}

interface BannerProps {
    saveKey?: string;
    w: "xs" | "sm" | "md" | "lg" | "xl" | "full";
    icon?: ReactNode;
    title: string;
    description: string;
    actions?: BannerAction[];
    variant?: "danger" | "warning" | "info";
}

export const Banner = ({
    saveKey,
    w,
    icon,
    title,
    description,
    variant,
    actions,
}: BannerProps) => {
    const navigate = useNavigate();
    const [isDismissed, setIsDismissed] = useState<boolean | null>(null);

    const lines = description.split("\n");

    const handleDismiss = () => {
        localStorage.setItem(`banner-${saveKey}-dismissed`, "true");
        setIsDismissed(true);
    };

    useEffect(() => {
        if (saveKey) {
            setIsDismissed(
                localStorage.getItem(`banner-${saveKey}-dismissed`) === "true"
            );
        }
    }, []);

    if (isDismissed === null || isDismissed) {
        return null;
    }

    return (
        <Container
            fluid={w === "full"}
            size={w === "full" ? undefined : w}
            mt="xl"
            mb="xl"
        >
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
                            <Group justify="flex-end" mt="xs">
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

                                            if (action.dismiss) {
                                                handleDismiss();
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
        </Container>
    );
};
