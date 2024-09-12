import { usePlaygroundFilesystem } from "@context/playground/hooks";
import { Tabs } from "@mantine/core";
import Markdown from "react-markdown";
import { FileEditor } from "./FileEditor";
import { useEffect, useRef, useState } from "react";

export const OpenFiles = () => {
    const openedRef = useRef<string[]>([]);
    const { openFiles } = usePlaygroundFilesystem();
    const [selectedFile, setSelectedFile] = useState<string | null>(null);

    useEffect(() => {
        // Figure out which file was opened, if any
        const opened = openFiles.filter(
            (path) => !openedRef.current.includes(path)
        );

        if (opened.length) {
            setSelectedFile(opened[0]);

            openedRef.current = openFiles;
        }
    }, [openFiles]);

    const FileTab = ({ path }: { path: string }) => {
        const fileName = path.split("/").pop();

        return <Tabs.Tab value={path}>{fileName}</Tabs.Tab>;
    };

    return (
        <Tabs
            value={selectedFile || "__welcome__"}
            w="100%"
            h="100%"
            onChange={setSelectedFile}
        >
            <Tabs.List>
                <Tabs.Tab value="__welcome__">Welcome</Tabs.Tab>
                {openFiles.map((path) => (
                    <FileTab key={path} path={path} />
                ))}
            </Tabs.List>

            <Tabs.Panel value="__welcome__">
                <Markdown>
                    {`
## Welcome to the Playground
You can create new files and directories using the file explorer on the left, or by using the command line.
`}
                </Markdown>
            </Tabs.Panel>

            {openFiles.map((path) => (
                <Tabs.Panel key={path} value={path} h="calc(100% - 14px)">
                    <FileEditor path={path} />
                </Tabs.Panel>
            ))}
        </Tabs>
    );
};
