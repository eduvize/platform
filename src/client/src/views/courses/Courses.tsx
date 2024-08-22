import {
    Center,
    Container,
    Divider,
    Flex,
    Grid,
    List,
    ScrollArea,
    Stack,
    ThemeIcon,
} from "@mantine/core";
import { InstructorSetup } from "./cta";
import { useInstructor } from "@context/user/hooks";
import { CoursePlanner } from "@views/course-planner";
import { Link, NavLink, Route, Routes, useMatches } from "react-router-dom";
import classes from "./Courses.module.css";

interface NavItemProps {
    to: string;
    label: string;
}

export const Courses = () => {
    const [instructor] = useInstructor();
    const matches = useMatches();

    console.log(matches);

    if (!instructor?.is_approved)
        return (
            <Container size="xs" p="xl">
                <InstructorSetup />
            </Container>
        );

    const NavItem = ({ to, label }: NavItemProps) => {
        return (
            <NavLink
                to={to}
                key={to}
                className={({ isActive, isPending }) => {
                    return isActive ? classes.active : undefined;
                }}
            >
                <List.Item className={classes.link} py="xs" px="sm">
                    {label}
                </List.Item>
            </NavLink>
        );
    };

    return (
        <Grid h="calc(100vh - 56px)">
            <Grid.Col
                span="content"
                bg="dark"
                h="calc(100vh - 56px)"
                style={{
                    borderRight: "1px solid var(--mantine-color-gray-7)",
                }}
            >
                <Stack justify="space-between" h="100%">
                    <List listStyleType="none" w="300px" p="sm">
                        <NavItem
                            to={"/dashboard/courses/active"}
                            label="My Courses"
                        />
                        <NavItem
                            to={"/dashboard/courses/previous"}
                            label="Completed Courses"
                        />
                    </List>

                    <List listStyleType="none" w="300px" p="sm">
                        <NavItem
                            to="/dashboard/courses/new"
                            label="Create a Course"
                        />
                    </List>
                </Stack>
            </Grid.Col>

            <Grid.Col span="auto">
                <ScrollArea.Autosize h="calc(100vh - 75px)">
                    <Center>
                        <Routes>
                            <Route
                                path="new"
                                handle="new"
                                element={<CoursePlanner />}
                            />
                        </Routes>
                    </Center>
                </ScrollArea.Autosize>
            </Grid.Col>
        </Grid>
    );
};
