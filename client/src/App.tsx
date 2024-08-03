import { createTheme, MantineProvider } from "@mantine/core";
import "./App.css";
import { Authentication, Dashboard, Home } from "./views";
import "@mantine/core/styles.css";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AuthProvider, useAuthenticated } from "./context";
import React from "react";

const AuthorizedRoute = ({ children }: { children: React.ReactNode }) => {
    const isAuthenticated = useAuthenticated();

    if (isAuthenticated) return <>{children}</>;
    else return <Authentication />;
};

const DashboardOrAuth = () => {
    return (
        <AuthorizedRoute>
            <Dashboard />
        </AuthorizedRoute>
    );
};

const router = createBrowserRouter([
    {
        path: "/",
        element: <Home />,
    },
    {
        path: "/auth",
        element: <Authentication />,
    },
    {
        path: "/dashboard/*",
        element: <DashboardOrAuth />,
        children: [
            { path: "courses", element: <DashboardOrAuth /> },
            { path: "profile", element: <DashboardOrAuth /> },
            { path: "jobs", element: <DashboardOrAuth /> },
            {
                path: "account/*",
                element: <DashboardOrAuth />,
                children: [{ path: "billing", element: <DashboardOrAuth /> }],
            },
        ],
    },
]);

function EduvizeApp() {
    const theme = createTheme({});

    return (
        <MantineProvider theme={theme} defaultColorScheme="dark">
            <AuthProvider>
                <RouterProvider router={router} />
            </AuthProvider>
        </MantineProvider>
    );
}

export default EduvizeApp;
