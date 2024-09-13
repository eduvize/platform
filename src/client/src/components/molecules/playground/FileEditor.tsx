import { useFile } from "@context/playground/hooks";
import Editor from "@monaco-editor/react";

interface FileEditorProps {
    path: string;
    height: string;
}

export const FileEditor = ({ height, path }: FileEditorProps) => {
    const { isLoaded, content, setContent } = useFile(path);

    return (
        <Editor
            height={height}
            theme="vs-dark"
            defaultLanguage="python"
            value={content}
            onChange={(evt) => setContent(evt || "")}
        />
    );
};
