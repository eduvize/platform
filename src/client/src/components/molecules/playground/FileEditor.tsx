import { useFile } from "@context/playground/hooks";
import Editor, { useMonaco } from "@monaco-editor/react";

interface FileEditorProps {
    path: string;
}

export const FileEditor = ({ path }: FileEditorProps) => {
    const { isLoaded, content, setContent } = useFile(path);

    return (
        <Editor
            height="100%"
            theme="vs-dark"
            defaultLanguage="python"
            value={content}
            onChange={(evt) => setContent(evt || "")}
        />
    );
};
