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
import { Lesson } from "@views/course";
import { Onboarding } from "@views/onboarding";
import { OnboardingProvider } from "@context/onboarding";
import { ChatProvider } from "@context/chat";
import { AudioInputProvider, AudioOutputProvider } from "@context/audio";

const CallToActionOrView = ({ children }: { children: React.ReactNode }) => {
    const { is_verified, is_profile_complete } = useOnboarding();
    if (!is_profile_complete) {
        return (
            <OnboardingProvider>
                <Onboarding />
            </OnboardingProvider>
        );
    }

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
            <AudioInputProvider>
                <AudioOutputProvider>
                    <ChatProvider>
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
                    </ChatProvider>
                </AudioOutputProvider>
            </AudioInputProvider>
        </UserProvider>
    );
};
