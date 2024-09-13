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
    rename: (path: string, newPath: string) => void;
    deletePath: (path: string) => void;
    openFile: (path: string) => void;
    closeFile: (path: string) => void;
    setFileContent: (path: string, content: string) => void;
    subscribeToOutput: (callback: (output: string) => void) => void;
    unsubscribeFromOutput: (callback: (output: string) => void) => void;
    isConnected: boolean;
    isReady: boolean;
    isReconnecting: boolean;
    environment?: PlaygroundEnvironment;
    openFiles: Record<string, string>;
};

const defaultValue: Context = {
    sendInput: () => {},
    resize: () => {},
    create: () => {},
    rename: () => {},
    deletePath: () => {},
    openFile: () => {},
    closeFile: () => {},
    setFileContent: () => {},
    subscribeToOutput: () => {},
    unsubscribeFromOutput: () => {},
    isConnected: false,
    isReady: false,
    isReconnecting: false,
    openFiles: {},
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
        const subscribersRef = useRef<((output: string) => void)[]>([]);
        const [isConnected, setIsConnected] = useState(false);
        const [isReconnecting, setIsReconnecting] = useState(false);
        const [isInstanceReady, setIsInstanceReady] = useState(false);
        const [environment, setEnvironment] = useState<PlaygroundEnvironment>();
        const [openFiles, setOpenFiles] = useState<Record<string, string>>({});

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
                    subscribersRef.current.forEach((cb) => cb(data));
                });

                clientRef.current.on(
                    "environment",
                    (data: PlaygroundEnvironment) => {
                        setEnvironment(data);
                    }
                );

                clientRef.current.on(
                    "file_content",
                    ({ path, content }: { path: string; content: string }) => {
                        setOpenFiles((prev) => ({ ...prev, [path]: content }));
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
            clientRef.current.emit("open_file", { path });
        };

        const handleRename = (path: string, newPath: string) => {
            if (!clientRef.current || !isInstanceReady) {
                return;
            }

            setOpenFiles((prev) => {
                const content = prev[path];
                const { [path]: _, ...rest } = prev;
                return { ...rest, [newPath]: content };
            });

            clientRef.current.emit("rename", { path, new_path: newPath });
        };

        const handleDeletePath = (path: string) => {
            if (!clientRef.current || !isInstanceReady) {
                return;
            }

            clientRef.current.emit("delete", { path });
        };

        const handleOpenFile = (path: string) => {
            if (!clientRef.current || !isInstanceReady) {
                return;
            }

            clientRef.current.emit("open_file", { path });
        };

        const handleCloseFile = (path: string) => {
            if (!clientRef.current || !isInstanceReady) {
                return;
            }

            setOpenFiles((prev) => {
                const { [path]: _, ...rest } = prev;
                return rest;
            });
        };

        const handleSetFileContent = (path: string, content: string) => {
            if (!clientRef.current || !isInstanceReady) {
                return;
            }

            clientRef.current.emit("save_file", { path, content });

            setOpenFiles((prev) => ({ ...prev, [path]: content }));
        };

        return (
            <PlaygroundContext.Provider
                value={{
                    sendInput: handleSendInput,
                    resize: handleResize,
                    create: handleCreate,
                    rename: handleRename,
                    deletePath: handleDeletePath,
                    openFile: handleOpenFile,
                    closeFile: handleCloseFile,
                    subscribeToOutput: (callback) =>
                        subscribersRef.current.push(callback),
                    unsubscribeFromOutput: (callback) =>
                        (subscribersRef.current = subscribersRef.current.filter(
                            (cb) => cb !== callback
                        )),
                    isConnected,
                    isReady: isInstanceReady,
                    isReconnecting,
                    environment,
                    openFiles,
                    setFileContent: handleSetFileContent,
                }}
            >
                {children}
            </PlaygroundContext.Provider>
        );
    }
);
