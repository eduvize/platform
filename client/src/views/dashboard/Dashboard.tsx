import { Container } from "@mantine/core";
import { SocketProvider } from "../../context";
import { Sidebar } from "./sections";

export const Dashboard = () => {
    return (
        <SocketProvider>
            <Sidebar />
        </SocketProvider>
    );
};
