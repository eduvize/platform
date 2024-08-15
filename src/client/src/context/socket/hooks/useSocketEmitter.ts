import { useContext, useEffect, useRef } from "react";
import { SocketContext } from "@context/socket";

export const useSocketEmitter = () => {
    const sendQueue = useRef<Map<string, any[]>>(new Map());
    const { socket, isConnected } = useContext(SocketContext);

    useEffect(() => {
        if (!socket || !isConnected) {
            return;
        }

        sendQueue.current.forEach((queue, event) => {
            queue.forEach((data) => {
                socket.emit(event, data);
            });
        });

        sendQueue.current.clear();
    }, [isConnected, socket]);

    return (event: string, data: any, queue: boolean = false) => {
        if (socket && isConnected) {
            socket.emit(event, data);
        } else if (queue) {
            const queue = sendQueue.current.get(event) || [];
            queue.push(data);
            sendQueue.current.set(event, queue);
        }
    };
};
