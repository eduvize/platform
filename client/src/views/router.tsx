import { useAuthenticated } from "../context";
import { Authentication } from "./authentication";
import { Dashboard } from "./dashboard";
import { Home } from "./home";

export const Router = () => {
    const isAuthenticated = useAuthenticated();

    if (isAuthenticated) return <Dashboard />;

    return <Home />;
};
