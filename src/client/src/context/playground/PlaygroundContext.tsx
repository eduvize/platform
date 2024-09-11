import { memo, useEffect, useRef, useState } from "react";
import io, { Socket } from "socket.io-client";
import { createContext } from "use-context-selector";
import { PlaygroundApi } from "@api";
import { PlaygroundEnvironment } from "@models/dto";
const SocketIOEndpoint = import.meta.env.VITE_SOCKETIO_ENDPOINT;

type Context = {
    sendInput: (command: string) => void;
    resize: (rows: number, columns: number) => void;
    create: (type: "file" | "directory", path: string) => void;
    output: string | null;
    isConnected: boolean;
    isReady: boolean;
    isReconnecting: boolean;
    environment?: PlaygroundEnvironment;
};

const defaultValue: Context = {
    sendInput: () => {},
    resize: () => {},
    create: () => {},
    output: null,
    isConnected: false,
    isReady: false,
    isReconnecting: false,
};

export const PlaygroundContext = createContext<Context>(defaultValue);

interface PlaygroundProviderProps {
    children: React.ReactNode;
}

export const PlaygroundProvider = memo(
    ({ children }: PlaygroundProviderProps) => {
        const sessionIdRef = useRef<string | null>(null);
        const clientRef = useRef<Socket | null>(null);
        const sizeRef = useRef<{ rows: number; columns: number }>({
            rows: 0,
            columns: 0,
        });
        const [isConnected, setIsConnected] = useState(false);
        const [isReconnecting, setIsReconnecting] = useState(false);
        const [isInstanceReady, setIsInstanceReady] = useState(false);
        const [output, setOutput] = useState<null | string>(null);
        const [environment, setEnvironment] = useState<PlaygroundEnvironment>();

        useEffect(() => {
            PlaygroundApi.createSession().then(({ session_id, token }) => {
                sessionIdRef.current = session_id;
                clientRef.current = io(SocketIOEndpoint, {
                    extraHeaders: {
                        Authorization: `Bearer ${token}`,
                    },
                    reconnection: true,
                    reconnectionAttempts: 99999,
                });

                clientRef.current.on("connect", () => {
                    setIsConnected(true);
                    console.log("Connected to playground server");
                });

                clientRef.current.on("disconnect", () => {
                    setIsReconnecting(true);
                    console.log("Disconnected from playground server");
                });

                clientRef.current.on("reconnect_attempt", () => {
                    setIsReconnecting(true);
                    console.log("Reconnecting to playground server");
                });

                clientRef.current.on("reconnect", () => {
                    setIsReconnecting(false);
                    console.log("Reconnected to playground server");
                });

                clientRef.current.on("instance_connected", () => {
                    setIsInstanceReady(true);
                    setIsReconnecting(false);
                    console.log("Instance is ready");

                    if (sizeRef.current.rows && sizeRef.current.columns) {
                        clientRef.current!.emit(
                            "terminal_resize",
                            sizeRef.current
                        );
                    }
                });

                clientRef.current.on("instance_disconnected", () => {
                    setIsInstanceReady(false);
                    setIsReconnecting(true);
                });

                clientRef.current.on("terminal_output", (data) => {
                    setOutput(data);
                });

                clientRef.current.on(
                    "environment",
                    (data: PlaygroundEnvironment) => {
                        setEnvironment(data);
                    }
                );
            });

            return () => {
                if (clientRef.current) {
                    clientRef.current.disconnect();
                }
            };
        }, []);

        const handleSendInput = (input: string) => {
            if (!clientRef.current || !isInstanceReady) {
                return;
            }

            clientRef.current.emit("terminal_input", input);
        };

        const handleResize = (rows: number, columns: number) => {
            sizeRef.current = { rows, columns };
            console.log(`terminal size set to ${rows}x${columns}`);

            if (!clientRef.current || !isInstanceReady) {
                return;
            }

            clientRef.current.emit("terminal_resize", { rows, columns });
        };

        const handleCreate = (type: "file" | "directory", path: string) => {
            if (!clientRef.current || !isInstanceReady) {
                return;
            }

            clientRef.current.emit("create", { type, path });
        };

        return (
            <PlaygroundContext.Provider
                value={{
                    sendInput: handleSendInput,
                    resize: handleResize,
                    create: handleCreate,
                    output,
                    isConnected,
                    isReady: isInstanceReady,
                    isReconnecting,
                    environment,
                }}
            >
                {children}
            </PlaygroundContext.Provider>
        );
    }
);
