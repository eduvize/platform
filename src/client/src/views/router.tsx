import { Authentication } from "./authentication";
import { Home } from "./home";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

const router = createBrowserRouter([
    {
        path: "/",
        element: <Home />,
    },
    {
        path: "/auth",
        element: <Authentication />,
    },
]);

export const Router = () => {
    return <RouterProvider router={router} />;
};
