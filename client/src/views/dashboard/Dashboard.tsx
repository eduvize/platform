import { Container, Stack } from "@mantine/core";
import { SocketProvider, UserProvider } from "../../context";
import { Header } from "./sections";
import { SetupCta, VerificationCta } from "./cta";
import { Route, Routes, useMatch } from "react-router-dom";
import { Courses, Profile } from "./views";
import { useCurrentUser, useOnboarding } from "../../context/user/hooks";

const CallToActionOrView = ({ children }: { children: React.ReactNode }) => {
    const isProfile = useMatch("/dashboard/profile");
    const { isOnboarded, isVerified } = useOnboarding();

    if (!isVerified) return <VerificationCta />;
    if (!isOnboarded && !isProfile) return <SetupCta />;

    return children;
};

export const Dashboard = () => {
    const { isOnboarded, isVerified } = useOnboarding();

    const containerWidth = !isOnboarded || !isVerified ? "lg" : "xl";

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
