import { Route, Routes, useMatch } from "react-router-dom";
import { UserProvider } from "@context/user";
import { useOnboarding } from "@context/user/hooks";
import { Profile } from "@views/profile";
import { Courses } from "@views/courses";
import { Header } from "./sections";
import { SetupCta, VerificationCta } from "./cta";

const CallToActionOrView = ({ children }: { children: React.ReactNode }) => {
    const isProfile = useMatch("/dashboard/profile");
    const { is_profile_complete, is_verified } = useOnboarding();

    if (!is_verified) return <VerificationCta />;
    if (!is_profile_complete && !isProfile) return <SetupCta />;

    return children;
};

export const Dashboard = () => {
    return (
        <UserProvider>
            <Header />

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
        </UserProvider>
    );
};
