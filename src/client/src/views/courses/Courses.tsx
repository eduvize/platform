import { Grid, ScrollArea, Card, Title } from "@mantine/core";
import { CoursePlanner } from "@views/course-planner";
import { Route, Routes, useMatch, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { CourseList } from "@organisms";

export const Courses = () => {
    const navigate = useNavigate();
    const isMainScreen = useMatch("/dashboard/courses");

    useEffect(() => {
        if (!isMainScreen) return;

        navigate("/dashboard/courses/active");
    }, [isMainScreen]);

    return (
        <Grid h="calc(100vh - 56px)">
            <Grid.Col span="auto">
                <ScrollArea.Autosize h="calc(100vh - 75px)">
                    <Routes>
                        <Route
                            path="active"
                            handle="active"
                            element={
                                <>
                                    <Card m="lg" withBorder p="xl" pl="md">
                                        <Title order={3} fw={500} c="white">
                                            My Courses
                                        </Title>
                                    </Card>
                                    <CourseList
                                        onNewCourseClick={() => {
                                            navigate("/dashboard/courses/new");
                                        }}
                                    />
                                </>
                            }
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
