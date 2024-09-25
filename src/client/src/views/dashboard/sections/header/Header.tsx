import { Link, NavLink } from "react-router-dom";
import logo from "../../logo.png";
import { Menu, Group, Center, Burger } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { IconChevronDown } from "@tabler/icons-react";
import classes from "./Header.module.css";
import { useLogout } from "@context/auth";

const links = [
    { link: "/dashboard/courses", label: "Courses" },
    {
        link: "/dashboard/profile",
        label: "Profile",
    },
    {
        link: "/dashboard/jobs",
        label: "Jobs",
    },
    {
        link: "#",
        label: "Account",
        links: [
            { link: "/dashboard/account/billing", label: "Billing" },
            { key: "logout", link: "#", label: "Sign out" },
        ],
    },
];

export function Header() {
    const logout = useLogout();
    const [opened, { toggle }] = useDisclosure(false);

    const getClickAction = (key?: string) => {
        if (!key) return () => {};

        if (key === "logout") {
            return logout;
        }

        return () => {};
    };

    const items = links.map((link) => {
        const menuItems = link.links?.map((item) => (
            <Menu.Item key={item.link} onClick={getClickAction(item.key)}>
                {item.label}
            </Menu.Item>
        ));

        if (menuItems) {
            return (
                <Menu
                    key={link.label}
                    trigger="hover"
                    transitionProps={{ exitDuration: 0 }}
                    withinPortal
                >
                    <Menu.Target>
                        <Link to="#" className={classes.link}>
                            <Center>
                                <span className={classes.linkLabel}>
                                    {link.label}
                                </span>
                                <IconChevronDown size="0.9rem" stroke={1.5} />
                            </Center>
                        </Link>
                    </Menu.Target>
                    <Menu.Dropdown>{menuItems}</Menu.Dropdown>
                </Menu>
            );
        }

        return (
            <NavLink
                key={link.label}
                to={link.link}
                className={({ isActive }) =>
                    `${classes.link} ${isActive ? classes.active : ""}`
                }
            >
                {link.label}
            </NavLink>
        );
    });

    return (
        <header className={classes.header}>
            <div className={classes.inner}>
                <img src={logo} style={{ height: "26px" }} />
                <Group gap={5} visibleFrom="sm">
                    {items}
                </Group>
                <Burger
                    opened={opened}
                    onClick={toggle}
                    size="sm"
                    hiddenFrom="sm"
                />
            </div>
        </header>
    );
}
