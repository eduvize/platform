import { Route, Routes, useMatch } from "react-router-dom";
import { SocketProvider } from "@context/socket";
import { UserProvider } from "@context/user";
import { useOnboarding } from "@context/user/hooks";
import { Container } from "@mantine/core";
import { Header } from "./sections";
import { SetupCta, VerificationCta } from "./cta";
import { Courses, Profile } from "./views";

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
            </UserProvider>
        </SocketProvider>
    );
};
