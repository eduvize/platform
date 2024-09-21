import React from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AuthProvider, useAuthenticated } from "@context/auth";
import { createTheme, MantineProvider } from "@mantine/core";
import { ContextMenuProvider } from "mantine-contextmenu";
import { Notifications } from "@mantine/notifications";
import { Authentication } from "@views/authentication";
import { Dashboard } from "@views/dashboard";
import { Home } from "@views/home";
import "./App.css";
import "@mantine/core/styles.css";
import "@mantine/dates/styles.css";
import "@mantine/notifications/styles.css";
import "mantine-contextmenu/styles.layer.css";
import { PlaygroundTest } from "@views/playground-test";

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
            {
                path: "courses/*",
                handle: "courses",
                element: <DashboardOrAuth />,
                children: [
                    {
                        path: "new",
                        handle: "new-course",
                        element: <DashboardOrAuth />,
                    },
                ],
            },
            {
                path: "profile",
                handle: "profile",
                element: <DashboardOrAuth />,
            },
            { path: "jobs", handle: "jobs", element: <DashboardOrAuth /> },
            {
                path: "account/*",
                element: <DashboardOrAuth />,
                children: [
                    {
                        path: "billing",
                        handle: "billing",
                        element: <DashboardOrAuth />,
                    },
                ],
            },
        ],
    },
    {
        path: "/playground-test",
        element: (
            <AuthorizedRoute>
                <PlaygroundTest />
            </AuthorizedRoute>
        ),
    },
]);

function EduvizeApp() {
    const theme = createTheme({});

    return (
        <MantineProvider theme={theme} defaultColorScheme="dark">
            <ContextMenuProvider>
                <Notifications />
                <AuthProvider>
                    <RouterProvider router={router} />
                </AuthProvider>
            </ContextMenuProvider>
        </MantineProvider>
    );
}

export default EduvizeApp;
