import { memo, ReactNode, useEffect, useRef, useState } from "react";
import io, { Socket } from "socket.io-client";
import { createContext } from "use-context-selector";
import { PlaygroundApi } from "@api";
import { FilesystemEntry, PlaygroundEnvironment } from "@models/dto";
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
    expandPath: (path: string) => void;
    collapsePath: (path: string) => void;
    isConnected: boolean;
    instanceState: "initializing" | "ready" | null;
    setupStatus: string | null;
    isReconnecting: boolean;
    environment?: PlaygroundEnvironment;
    openFiles: Record<string, string>;
    readme?: ReactNode | string;
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
    expandPath: () => {},
    collapsePath: () => {},
    isConnected: false,
    instanceState: null,
    setupStatus: null,
    isReconnecting: false,
    openFiles: {},
};

export const PlaygroundContext = createContext<Context>(defaultValue);

interface PlaygroundProviderProps {
    environmentId: string;
    onExerciseObjectiveStatusChange?: (
        objectiveId: string,
        isCompleted: boolean
    ) => void;
    readme: ReactNode | string;
    children: React.ReactNode;
}

export const PlaygroundProvider = memo(
    ({
        environmentId,
        onExerciseObjectiveStatusChange,
        readme,
        children,
    }: PlaygroundProviderProps) => {
        const sessionIdRef = useRef<string | null>(null);
        const clientRef = useRef<Socket | null>(null);
        const sizeRef = useRef<{ rows: number; columns: number }>({
            rows: 0,
            columns: 0,
        });
        const subscribersRef = useRef<((output: string) => void)[]>([]);
        const [isConnected, setIsConnected] = useState(false);
        const [isReconnecting, setIsReconnecting] = useState(false);
        const [instanceState, setInstanceState] = useState<
            "initializing" | "ready" | null
        >(null);
        const [setupStatus, setSetupStatus] = useState<string | null>(null);
        const [environment, setEnvironment] = useState<PlaygroundEnvironment>({
            filesystem: [],
        });
        const [openFiles, setOpenFiles] = useState<Record<string, string>>({});

        useEffect(() => {
            PlaygroundApi.createSession(environmentId).then(
                ({ session_id, token }) => {
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
                        setInstanceState("initializing");
                        setSetupStatus(null);
                        setIsReconnecting(false);

                        if (sizeRef.current.rows && sizeRef.current.columns) {
                            clientRef.current!.emit(
                                "terminal_resize",
                                sizeRef.current
                            );
                        }
                    });

                    clientRef.current.on(
                        "exercise_objective_status",
                        ({ objective_id, is_completed }) => {
                            console.log(
                                `Objective ${objective_id} is completed: ${is_completed}`
                            );

                            onExerciseObjectiveStatusChange?.(
                                objective_id,
                                is_completed
                            );
                        }
                    );

                    clientRef.current.on("setup_status", (status) => {
                        setSetupStatus(status);
                    });

                    clientRef.current.on("instance_ready", () => {
                        handleExpandPath("/");
                        setInstanceState("ready");
                        setSetupStatus(null);
                    });

                    clientRef.current.on("instance_disconnected", () => {
                        setInstanceState(null);
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
                        ({
                            path,
                            content,
                        }: {
                            path: string;
                            content: string;
                        }) => {
                            setOpenFiles((prev) => ({
                                ...prev,
                                [path]: content,
                            }));
                        }
                    );

                    clientRef.current.on(
                        "directory_contents",
                        ({ path, entries }) => {
                            setEnvironment((prevEnvironment) => {
                                if (path === "") {
                                    return {
                                        ...prevEnvironment,
                                        filesystem: [
                                            ...prevEnvironment.filesystem.filter(
                                                (e: FilesystemEntry) =>
                                                    entries.find(
                                                        (f: FilesystemEntry) =>
                                                            f.path === e.path
                                                    )
                                            ),
                                            ...entries.filter(
                                                (e: FilesystemEntry) =>
                                                    !prevEnvironment.filesystem.find(
                                                        (f) => f.path === e.path
                                                    )
                                            ),
                                        ],
                                    };
                                }

                                // Helper function to recursively merge entries at the target path
                                const mergeEntriesAtPath = (
                                    nodes: FilesystemEntry[],
                                    targetPath: string,
                                    entriesToMerge: FilesystemEntry[]
                                ): FilesystemEntry[] => {
                                    return nodes.map((node) => {
                                        if (
                                            node.path === targetPath &&
                                            node.type === "directory"
                                        ) {
                                            // Replace or set the children of the target directory
                                            return {
                                                ...node,
                                                children: [
                                                    ...(
                                                        node.children || []
                                                    ).filter((e) =>
                                                        entriesToMerge.find(
                                                            (f) =>
                                                                f.path ===
                                                                e.path
                                                        )
                                                    ),
                                                    ...entriesToMerge.filter(
                                                        (e) =>
                                                            !node.children?.find(
                                                                (f) =>
                                                                    f.path ===
                                                                    e.path
                                                            )
                                                    ),
                                                ],
                                            };
                                        } else if (node.children) {
                                            // Recursively search in nested directories
                                            return {
                                                ...node,
                                                children: mergeEntriesAtPath(
                                                    node.children,
                                                    targetPath,
                                                    entriesToMerge
                                                ),
                                            };
                                        } else {
                                            return node;
                                        }
                                    });
                                };

                                const updatedFilesystem = mergeEntriesAtPath(
                                    prevEnvironment.filesystem,
                                    path,
                                    entries
                                );

                                return {
                                    ...prevEnvironment,
                                    filesystem: updatedFilesystem,
                                };
                            });
                        }
                    );
                }
            );

            return () => {
                if (clientRef.current) {
                    clientRef.current.disconnect();
                }
            };
        }, []);

        const isPathLoaded = (path: string) => {
            // Helper function to recursively check if the path has loaded children
            const checkPath = (
                nodes: FilesystemEntry[],
                targetPath: string
            ) => {
                for (const node of nodes) {
                    if (node.path === targetPath && node.type === "directory") {
                        // Check if children are defined and not empty
                        return node.children && node.children.length > 0;
                    } else if (node.children) {
                        // Continue searching in nested directories
                        const result = checkPath(node.children, targetPath);
                        if (result) return true;
                    }
                }
                return false;
            };

            return checkPath(environment?.filesystem || [], path);
        };

        const handleSendInput = (input: string) => {
            if (!clientRef.current || instanceState !== "ready") {
                return;
            }

            clientRef.current.emit("terminal_input", input);
        };

        const handleResize = (rows: number, columns: number) => {
            sizeRef.current = { rows, columns };
            console.log(`terminal size set to ${rows}x${columns}`);

            if (!clientRef.current || instanceState !== "ready") {
                return;
            }

            clientRef.current.emit("terminal_resize", { rows, columns });
        };

        const handleCreate = (type: "file" | "directory", path: string) => {
            if (!clientRef.current || instanceState !== "ready") {
                return;
            }

            clientRef.current.emit("create", { type, path });

            // get the parent path
            const parentPath = path.split("/").slice(0, -1).join("/");

            if (type === "file") {
                clientRef.current.emit("open_file", { path });
            }

            if (!isPathLoaded(parentPath)) {
                handleExpandPath(parentPath);
            }
        };

        const handleRename = (path: string, newPath: string) => {
            if (!clientRef.current || instanceState !== "ready") {
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
            if (!clientRef.current || instanceState !== "ready") {
                return;
            }

            clientRef.current.emit("delete", { path });
        };

        const handleOpenFile = (path: string) => {
            if (!clientRef.current || instanceState !== "ready") {
                return;
            }

            clientRef.current.emit("open_file", { path });
        };

        const handleCloseFile = (path: string) => {
            if (!clientRef.current || instanceState !== "ready") {
                return;
            }

            setOpenFiles((prev) => {
                const { [path]: _, ...rest } = prev;
                return rest;
            });
        };

        const handleSetFileContent = (path: string, content: string) => {
            if (!clientRef.current || instanceState !== "ready") {
                return;
            }

            clientRef.current.emit("save_file", { path, content });

            setOpenFiles((prev) => ({ ...prev, [path]: content }));
        };

        const handleExpandPath = (path: string) => {
            if (!clientRef.current || instanceState !== "ready") {
                return;
            }

            clientRef.current.emit("get_directory", { path });
            clientRef.current.emit("subscribe_to_path", { path });
        };

        const handleCollapsePath = (path: string) => {
            setEnvironment((prevEnvironment) => {
                const updatedFilesystem = [...prevEnvironment.filesystem];

                // Helper function to recursively find the correct path and clear its children
                const clearChildrenAtPath = (
                    nodes: FilesystemEntry[],
                    targetPath: string
                ): FilesystemEntry[] => {
                    return nodes.map((node) => {
                        if (
                            node.path === targetPath &&
                            node.type === "directory"
                        ) {
                            return { ...node, children: [] };
                        } else if (node.children) {
                            return {
                                ...node,
                                children: clearChildrenAtPath(
                                    node.children,
                                    targetPath
                                ),
                            };
                        }
                        return node;
                    }) as FilesystemEntry[];
                };

                const newFilesystem = clearChildrenAtPath(
                    updatedFilesystem,
                    path
                );
                return { ...prevEnvironment, filesystem: newFilesystem };
            });

            if (!clientRef.current || instanceState !== "ready") {
                return;
            }

            clientRef.current.emit("unsubscribe_from_path", { path });
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
                    expandPath: handleExpandPath,
                    collapsePath: handleCollapsePath,
                    isConnected,
                    instanceState,
                    setupStatus,
                    isReconnecting,
                    environment,
                    openFiles,
                    setFileContent: handleSetFileContent,
                    readme,
                }}
            >
                {children}
            </PlaygroundContext.Provider>
        );
    }
);
