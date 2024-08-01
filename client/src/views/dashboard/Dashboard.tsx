import { SocketProvider } from "../../context";

export const Dashboard = () => {
    return (
        <SocketProvider>
            <h1>Dashboard</h1>
        </SocketProvider>
    );
};
