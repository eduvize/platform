import { Grid, List, ScrollArea, Stack } from "@mantine/core";
import { CoursePlanner } from "@views/course-planner";
import {
    NavLink,
    Route,
    Routes,
    useMatch,
    useNavigate,
} from "react-router-dom";
import classes from "./Courses.module.css";
import { useEffect } from "react";
import { CourseList } from "@organisms";

interface NavItemProps {
    to: string;
    label: string;
}

export const Courses = () => {
    const navigate = useNavigate();
    const isMainScreen = useMatch("/dashboard/courses");

    useEffect(() => {
        if (!isMainScreen) return;

        navigate("/dashboard/courses/active");
    }, [isMainScreen]);

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
                    <Routes>
                        <Route
                            path="active"
                            handle="active"
                            element={<CourseList />}
                        />
                        <Route
                            path="new"
                            handle="new"
                            element={<CoursePlanner />}
                        />
                    </Routes>
                </ScrollArea.Autosize>
            </Grid.Col>
        </Grid>
    );
};
