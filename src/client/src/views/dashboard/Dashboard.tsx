import { Route, Routes, useMatch, useNavigate } from "react-router-dom";
import { UserProvider } from "@context/user";
import { useOnboarding } from "@context/user/hooks";
import { Profile } from "@views/profile";
import { Header } from "./sections";
import { VerificationCta } from "./cta";
import { useEffect } from "react";
import { Box, Container } from "@mantine/core";
import { Courses } from "@views/courses";
import { Course } from "@views/course";
import { Lesson } from "@views/lesson";

const CallToActionOrView = ({ children }: { children: React.ReactNode }) => {
    const { is_verified } = useOnboarding();

    if (!is_verified) {
        return (
            <Container size="md" p="xl">
                <VerificationCta />
            </Container>
        );
    }

    return children;
};

export const Dashboard = () => {
    const navigate = useNavigate();
    const isDashboardRoot = useMatch("/dashboard");

    useEffect(() => {
        if (isDashboardRoot) {
            navigate("/dashboard/courses");
        }
    }, []);

    return (
        <UserProvider>
            <Header />

            <Box pt="56px">
                <Routes>
                    <Route
                        path="course/:course_id/lesson/:lesson_id"
                        handle="lesson"
                        element={
                            <CallToActionOrView>
                                <Lesson />
                            </CallToActionOrView>
                        }
                    />
                    <Route
                        path="course/:course_id"
                        handle="course"
                        element={
                            <CallToActionOrView>
                                <Course />
                            </CallToActionOrView>
                        }
                    />
                    <Route
                        path="courses/*"
                        handle="courses"
                        element={
                            <CallToActionOrView>
                                <Courses />
                            </CallToActionOrView>
                        }
                    />
                    <Route
                        path="profile"
                        handle="profile"
                        element={
                            <CallToActionOrView>
                                <Profile />
                            </CallToActionOrView>
                        }
                    />
                </Routes>
            </Box>
        </UserProvider>
    );
};
