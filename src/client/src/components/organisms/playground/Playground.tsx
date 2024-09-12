import { useEffect, useRef, useState } from "react";
import {
    useCommandLine,
    usePlaygroundConnectivity,
} from "@context/playground/hooks";
import {
    Card,
    Text,
    Stack,
    Center,
    Loader,
    Grid,
    Group,
    Box,
} from "@mantine/core";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import "./Playground.css";
import { FileEditor, FileExplorer, OpenFiles } from "@molecules";

interface PlaygroundProps {
    hideTerminal?: boolean;
}

export const Playground = ({ hideTerminal }: PlaygroundProps) => {
    const viewport = useRef<HTMLDivElement>(null);
    const terminalRef = useRef<Terminal | null>(null);
    const fitAddonRef = useRef<FitAddon>(new FitAddon());
    const { connected, ready, reconnecting } = usePlaygroundConnectivity();
    const { sendInput, resize, output } = useCommandLine();
    const [showTerminal, setShowTerminal] = useState(!hideTerminal);

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

    if (!connected || !ready || reconnecting) {
        return (
            <Card withBorder mih="400px">
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
            </Card>
        );
    }

    return (
        <Card withBorder p={0}>
            <Grid>
                <Grid.Col span={12}>
                    <Group h="400px" wrap="nowrap" align="flex-start">
                        <FileExplorer w="200px" />
                        <OpenFiles />
                    </Group>
                </Grid.Col>

                {showTerminal && (
                    <Grid.Col span="auto">
                        <Box p="sm">
                            <div ref={viewport} style={{ height: "200px" }} />
                        </Box>
                    </Grid.Col>
                )}
            </Grid>
        </Card>
    );
};
