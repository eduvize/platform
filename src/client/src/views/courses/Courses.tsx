import { Text, Grid, ScrollArea, Card, Title } from "@mantine/core";
import { CoursePlanner } from "@views/course-planner";
import { Route, Routes, useMatch, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { CourseList } from "@organisms";
import { useOnboarding } from "@context/user/hooks";
import { Banner } from "@molecules";
import { IconAlertTriangle } from "@tabler/icons-react";

export const Courses = () => {
    const navigate = useNavigate();
    const { is_profile_complete } = useOnboarding();
    const isMainScreen = useMatch("/dashboard/courses");

    useEffect(() => {
        if (!isMainScreen) return;

        navigate("/dashboard/courses/active");
    }, [isMainScreen]);

    return (
        <Grid h="calc(100vh - 56px)">
            <Grid.Col span="auto">
                <ScrollArea.Autosize h="calc(100vh - 75px)">
                    {!is_profile_complete && (
                        <Banner
                            saveKey="profile_complete_banner_courses"
                            w="sm"
                            icon={<IconAlertTriangle />}
                            title="You haven't completed your profile"
                            description={`
In order to get the most out of the platform, it's recommended you complete your profile.

We leverage this information to provide you with the best possible experience, including personalized course recommendations and more.
`}
                            variant="warning"
                            actions={[
                                {
                                    label: "Dismiss",
                                    dismiss: true,
                                },
                                {
                                    label: "Go to profile",
                                    href: "/dashboard/profile",
                                },
                            ]}
                        />
                    )}

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
