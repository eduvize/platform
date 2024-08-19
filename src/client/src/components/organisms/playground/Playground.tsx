import { useEffect, useRef } from "react";
import { useCommandLine, usePlaygroundState } from "@context/playground/hooks";
import { Card, Text, Stack, Center, Loader } from "@mantine/core";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import "./Playground.css";

export const Playground = () => {
    const viewport = useRef<HTMLDivElement>(null);
    const terminalRef = useRef<Terminal | null>(null);
    const fitAddonRef = useRef<FitAddon>(new FitAddon());
    const { connected, ready, reconnecting } = usePlaygroundState();
    const { sendInput, resize, output } = useCommandLine();

    useEffect(() => {
        if (!connected || reconnecting) {
            if (terminalRef.current) {
                terminalRef.current.dispose();
                terminalRef.current = null;
            }

            return;
        }

        if (!ready || terminalRef.current) {
            return;
        }

        terminalRef.current = new Terminal();

        terminalRef.current.loadAddon(fitAddonRef.current);
        terminalRef.current.open(viewport.current!);
        fitAddonRef.current.fit();

        terminalRef.current.onData((data) => {
            sendInput(data);
        });

        terminalRef.current.onResize(({ rows, cols }) => {
            fitAddonRef.current.fit();
            resize(rows, cols);
        });

        const { rows, cols } = terminalRef.current;

        resize(rows, cols);
    }, [connected, ready, reconnecting]);

    const handleScrollToBottom = () => {
        viewport.current?.scrollTo({
            top: viewport.current.scrollHeight,
            behavior: "smooth",
        });
    };

    useEffect(() => {
        if (!terminalRef.current || !output) return;

        terminalRef.current.write(output);

        handleScrollToBottom();
    }, [output]);

    return (
        <Card withBorder mih="400px">
            {(!connected || !ready || reconnecting) && (
                <Center pos="absolute" left="0" top="0" w="100%" h="100%">
                    <Stack align="center">
                        <Loader type="bars" size="lg" />

                        <Text mt="lg" ta="center">
                            {reconnecting && "Session lost. Reconnecting..."}

                            {!reconnecting && (
                                <>
                                    {!connected
                                        ? "Connecting to playground..."
                                        : "Initializing playground..."}
                                </>
                            )}
                        </Text>
                    </Stack>
                </Center>
            )}

            {connected && ready && !reconnecting && (
                <div ref={viewport} style={{ height: "400px" }} />
            )}
        </Card>
    );
};
