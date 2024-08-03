import { Container, Notification, Stack } from "@mantine/core";
import { SocketProvider, UserProvider } from "../../context";
import { Header } from "./sections";
import { SetupCta, VerificationCta } from "./cta";
import { Route, Routes, useMatch } from "react-router-dom";
import { Courses, Profile } from "./views";
import { useOnboarding } from "../../context/user/hooks";

const CallToActionOrView = ({ children }: { children: React.ReactNode }) => {
    const isProfile = useMatch("/dashboard/profile");
    const { is_profile_complete, is_verified } = useOnboarding();

    if (!is_verified) return <VerificationCta />;
    if (!is_profile_complete && !isProfile) return <SetupCta />;

    return children;
};

export const Dashboard = () => {
    const { is_profile_complete, is_verified } = useOnboarding();

    const containerWidth = !is_profile_complete || !is_verified ? "lg" : "xl";

    return (
        <SocketProvider>
            <UserProvider>
                <Stack h="100vh">
                    <Header />

                    <Container size={containerWidth}>
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
                </Stack>
            </UserProvider>
        </SocketProvider>
    );
};
