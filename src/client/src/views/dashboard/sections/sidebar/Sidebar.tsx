import { useState } from "react";
import { Tooltip, UnstyledButton, Stack, rem } from "@mantine/core";
import {
    IconHome2,
    IconSettings,
    IconLogout,
    IconIdBadge2,
    IconBooks,
} from "@tabler/icons-react";
import classes from "./Sidebar.module.css";

interface NavbarLinkProps {
    icon: typeof IconHome2;
    label: string;
    active?: boolean;
    onClick?(): void;
}

function NavbarLink({ icon: Icon, label, active, onClick }: NavbarLinkProps) {
    return (
        <Tooltip
            label={label}
            position="right"
            transitionProps={{ duration: 0 }}
        >
            <UnstyledButton
                onClick={onClick}
                className={classes.link}
                data-active={active || undefined}
            >
                <Icon
                    style={{ width: rem(24), height: rem(24) }}
                    stroke={1.5}
                />
            </UnstyledButton>
        </Tooltip>
    );
}

const mockdata = [
    { icon: IconHome2, label: "Home" },
    { icon: IconIdBadge2, label: "Your profile" },
    { icon: IconBooks, label: "Your courses" },
];

export function Sidebar() {
    const [active, setActive] = useState(2);

    const links = mockdata.map((link, index) => (
        <NavbarLink
            {...link}
            key={link.label}
            active={index === active}
            onClick={() => setActive(index)}
        />
    ));

    return (
        <nav className={classes.navbar}>
            <div className={classes.navbarMain}>
                <Stack justify="center" gap={24}>
                    {links}
                </Stack>
            </div>

            <Stack justify="center" gap={0}>
                <NavbarLink icon={IconSettings} label="Settings" />
                <NavbarLink icon={IconLogout} label="Logout" />
            </Stack>
        </nav>
    );
}
