import { Route, Routes, useMatch } from "react-router-dom";
import { UserProvider } from "@context/user";
import { useOnboarding } from "@context/user/hooks";
import { Profile } from "@views/profile";
import { Courses } from "@views/courses";
import { Card, Container } from "@mantine/core";
import { Header } from "./sections";
import { SetupCta, VerificationCta } from "./cta";
import { Playground } from "@organisms";
import { PlaygroundProvider } from "@context/playground";

const CallToActionOrView = ({ children }: { children: React.ReactNode }) => {
    const isProfile = useMatch("/dashboard/profile");
    const { is_profile_complete, is_verified } = useOnboarding();

    if (!is_verified) return <VerificationCta />;
    if (!is_profile_complete && !isProfile) return <SetupCta />;

    return children;
};

export const Dashboard = () => {
    const { is_profile_complete, is_verified } = useOnboarding();
    const isCourses = useMatch("/dashboard/courses");

    const containerWidth = !is_profile_complete || !is_verified ? "lg" : "xl";

    return (
        <UserProvider>
            <Header />

            <PlaygroundProvider>
                <Playground />
            </PlaygroundProvider>

            <Container size={containerWidth} fluid={!!isCourses}>
                <Routes>
                    <Route
                        path="/"
                        element={
                            <CallToActionOrView>
                                <Courses />
                            </CallToActionOrView>
                        }
                    />
                    <Route
                        path="courses"
                        element={
                            <CallToActionOrView>
                                <Courses />
                            </CallToActionOrView>
                        }
                    />
                    <Route
                        path="profile"
                        element={
                            <CallToActionOrView>
                                <Profile />
                            </CallToActionOrView>
                        }
                    />
                </Routes>
            </Container>
        </UserProvider>
    );
};
