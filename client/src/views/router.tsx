import { useAuthenticated } from "../context";
import { Authentication } from "./authentication";
import { Dashboard } from "./dashboard";

export const Router = () => {
    const isAuthenticated = useAuthenticated();

    if (isAuthenticated) return <Dashboard />;

    return <Authentication />;
};
