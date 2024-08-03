import { Container, Stack } from "@mantine/core";
import { SocketProvider } from "../../context";
import { Header } from "./sections";
import classes from "./Dashboard.module.css";
import { SetupCta } from "./cta";
import { Route, Routes, useMatch } from "react-router-dom";
import { Courses, Profile } from "./views";

const CallToActionOrView = ({ children }: { children: React.ReactNode }) => {
    const isProfile = useMatch("/dashboard/profile");

    const hasDoneProfile = false;

    if (!hasDoneProfile && !isProfile) return <SetupCta />;

    return children;
};

export const Dashboard = () => {
    return (
        <SocketProvider>
            <Stack h="100vh">
                <Header />

                <Container>
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
        </SocketProvider>
    );
};
