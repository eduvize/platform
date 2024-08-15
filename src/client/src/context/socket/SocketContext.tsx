import { createContext, useEffect, useState } from "react";
import { io, Socket } from "socket.io-client";
import { useAuthToken } from "@context/auth/hooks";

type Context = {
    socket: Socket | null;
    isConnected: boolean;
};

const defaultValue: Context = {
    socket: null,
    isConnected: false,
};

export const SocketContext = createContext<Context>(defaultValue);

interface SocketProviderProps {
    children: React.ReactNode;
}

export const SocketProvider = ({ children }: SocketProviderProps) => {
    const [socket, setSocket] = useState<Socket | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const authToken = useAuthToken();

    useEffect(() => {
        const socket = io("http://localhost:8000", {
            auth: {
                token: authToken,
            },
            transports: ["websocket"],
            addTrailingSlash: true,
        });

        socket.on("connect", () => {
            console.log("Connected to server");
            setIsConnected(true);
        });

        socket.on("disconnect", () => {
            console.log("Disconnected from server");
            setIsConnected(false);
        });

        setSocket(socket);

        return () => {
            socket.disconnect();
        };
    }, [authToken]);

    return (
        <SocketContext.Provider
            value={{
                socket,
                isConnected,
            }}
        >
            {children}
        </SocketContext.Provider>
    );
};
