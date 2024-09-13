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
    Flex,
} from "@mantine/core";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import "./Playground.css";
import { FileExplorer, OpenFiles } from "@molecules";
import { useResizeObserver } from "@mantine/hooks";

interface PlaygroundProps {
    hideTerminal?: boolean;
    height?: number | string;
}

export const Playground = ({ hideTerminal, height }: PlaygroundProps) => {
    const viewport = useRef<HTMLDivElement>(null);
    const terminalRef = useRef<Terminal | null>(null);
    const [stackRef, rect] = useResizeObserver();
    const editorContainerRef = useRef<HTMLDivElement>(null);
    const fitAddonRef = useRef<FitAddon>(new FitAddon());
    const { connected, ready, reconnecting } = usePlaygroundConnectivity();
    const { sendInput, resize, subscribe, unsubscribe } = useCommandLine();
    const [showTerminal, setShowTerminal] = useState(!hideTerminal);
    const [focusedFile, setFocusedFile] = useState<string | null>(null);
    const [editorHeight, setEditorHeight] = useState<number | null>(null);
    const [terminalHeight, setTerminalHeight] = useState<number>(130);

    const heightProperty =
        typeof height === "number"
            ? `${height}px`
            : typeof height === "string"
            ? height
            : "400px";

    useEffect(() => {
        if (rect) {
            const { width, height } = rect;

            setEditorHeight(height - terminalHeight);
        }
    }, [rect]);

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

        terminalRef.current = new Terminal({
            cursorBlink: true,
            macOptionIsMeta: true,
        });

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

    useEffect(() => {
        // Subscribe to output
        const handleOutput = (output: string) => {
            if (!terminalRef.current) return;

            terminalRef.current.write(output);

            handleScrollToBottom();
        };

        subscribe(handleOutput);

        return () => {
            unsubscribe(handleOutput);
        };
    }, []);

    const handleScrollToBottom = () => {
        viewport.current?.scrollTo({
            top: viewport.current.scrollHeight,
            behavior: "smooth",
        });
    };

    if (!connected || !ready || reconnecting) {
        return (
            <Card withBorder mih={heightProperty}>
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
                    <Group
                        gap="xs"
                        h={heightProperty}
                        wrap="nowrap"
                        align="flex-start"
                    >
                        <Box bg="dark" h="100%">
                            <FileExplorer
                                w="200px"
                                onSelect={(type, path) => {
                                    if (type === "file") {
                                        setFocusedFile(path);
                                    }
                                }}
                            />
                        </Box>

                        <Stack w="100%" h="100%" ref={stackRef} gap={0}>
                            <OpenFiles
                                selectedFile={focusedFile}
                                height={`${editorHeight}px`}
                            />

                            {showTerminal && (
                                <div
                                    ref={viewport}
                                    style={{
                                        height: `${terminalHeight}px`,
                                        width: "100%",
                                        borderTop:
                                            "1px solid var(--mantine-color-gray-7)",
                                        padding: "4px",
                                    }}
                                />
                            )}
                        </Stack>
                    </Group>
                </Grid.Col>
            </Grid>
        </Card>
    );
};
