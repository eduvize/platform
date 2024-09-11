import Editor, { useMonaco } from "@monaco-editor/react";

export const FileEditor = () => {
    return (
        <Editor
            height="100%"
            theme="vs-dark"
            defaultLanguage="python"
            defaultValue="// Write your code"
        />
    );
};
