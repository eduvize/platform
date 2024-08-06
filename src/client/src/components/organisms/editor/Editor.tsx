import { Editor as Monaco } from "@monaco-editor/react";
import classes from "./Editor.module.css";

export const Editor = () => {
    return (
        <Monaco
            height="90vh"
            defaultLanguage="javascript"
            theme="vs-dark"
            defaultValue="// some comment"
        />
    );
};
