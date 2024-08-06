import { Anchor, Group, ActionIcon, rem } from "@mantine/core";
import {
    IconBrandTwitter,
    IconBrandYoutube,
    IconBrandInstagram,
} from "@tabler/icons-react";
import classes from "./Footer.module.css";
import logo from "./logo.png";

const links = [
    { link: "#", label: "About" },
    { link: "#", label: "Privacy" },
    { link: "#", label: "GitHub" },
    { link: "#", label: "Pricing" },
];

export function Footer() {
    const items = links.map((link) => (
        <Anchor
            c="dimmed"
            key={link.label}
            href={link.link}
            lh={1}
            onClick={(event) => event.preventDefault()}
            size="sm"
        >
            {link.label}
        </Anchor>
    ));

    return (
        <div className={classes.footer}>
            <div className={classes.inner}>
                <img src={logo} alt="Logo" className={classes.logo} />

                <Group className={classes.links}>{items}</Group>
            </div>
        </div>
    );
}
