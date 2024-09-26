import { useFile } from "@context/playground/hooks";
import Editor from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import { loader } from "@monaco-editor/react";
import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import { useMemo } from "react";

interface FileEditorProps {
    path: string;
    height: string;
}

enum Language {
    Json = "json",
    Javascript = "javascript",
    Css = "css",
    Html = "html",
    Typescript = "typescript",
    Rust = "rust",
    Coffee = "coffee",
    Bat = "bat",
    Bicep = "bicep",
    Clojure = "clojure",
    Cpp = "cpp",
    Csharp = "csharp",
    Dart = "dart",
    Dockerfile = "dockerfile",
    Elixir = "elixir",
    Fsharp = "fsharp",
    Go = "go",
    Graphql = "graphql",
    Handlebars = "handlebars",
    Ini = "ini",
    Java = "java",
    Kotlin = "kotlin",
    Less = "less",
    Lua = "lua",
    Markdown = "markdown",
    ObjectiveC = "objective-c",
    Pascal = "pascal",
    Perl = "perl",
    Php = "php",
    Powershell = "powershell",
    Protobuf = "protobuf",
    Pug = "pug",
    Python = "python",
    R = "r",
    Razor = "razor",
    Ruby = "ruby",
    Scala = "scala",
    Sass = "sass",
    Shell = "shell",
    Sql = "sql",
    Swift = "swift",
    Vb = "vb",
    Xml = "xml",
    Yaml = "yaml",
}

function getWorkerDynamic(
    name: string,
    worker: string,
    base: "basic-languages" | "language"
) {
    const url = `monaco-editor/esm/vs/${base}/${name}/${worker}.worker?worker`;

    return new Worker(new URL(url, import.meta.url), {
        type: "module",
    } as WorkerOptions);
}

self.MonacoEnvironment = {
    getWorker(_, label) {
        switch (label) {
            case Language.Json:
                return getWorkerDynamic("json", "json", "language");
            case Language.Css:
                return getWorkerDynamic("css", "css", "language");
            case Language.Html:
                return getWorkerDynamic("html", "html", "language");
            case Language.Typescript:
                return getWorkerDynamic("typescript", "ts", "language");
            case Language.Rust:
                return getWorkerDynamic("rust", "rust", "basic-languages");
            case Language.Coffee:
                return getWorkerDynamic("coffee", "coffee", "basic-languages");
            case Language.Bat:
                return getWorkerDynamic("bat", "bat", "basic-languages");
            case Language.Bicep:
                return getWorkerDynamic("bicep", "bicep", "basic-languages");
            case Language.Clojure:
                return getWorkerDynamic(
                    "clojure",
                    "clojure",
                    "basic-languages"
                );
            case Language.Cpp:
                return getWorkerDynamic("cpp", "cpp", "basic-languages");
            case Language.Csharp:
                return getWorkerDynamic("csharp", "csharp", "basic-languages");
            case Language.Dart:
                return getWorkerDynamic("dart", "dart", "basic-languages");
            case Language.Dockerfile:
                return getWorkerDynamic(
                    "dockerfile",
                    "dockerfile",
                    "basic-languages"
                );
            case Language.Elixir:
                return getWorkerDynamic("elixir", "elixir", "basic-languages");
            case Language.Fsharp:
                return getWorkerDynamic("fsharp", "fsharp", "basic-languages");
            case Language.Go:
                return getWorkerDynamic("go", "go", "basic-languages");
            case Language.Graphql:
                return getWorkerDynamic(
                    "graphql",
                    "graphql",
                    "basic-languages"
                );
            case Language.Handlebars:
                return getWorkerDynamic(
                    "handlebars",
                    "handlebars",
                    "basic-languages"
                );
            case Language.Ini:
                return getWorkerDynamic("ini", "ini", "basic-languages");
            case Language.Java:
                return getWorkerDynamic("java", "java", "basic-languages");
            case Language.Kotlin:
                return getWorkerDynamic("kotlin", "kotlin", "basic-languages");
            case Language.Less:
                return getWorkerDynamic("less", "less", "basic-languages");
            case Language.Lua:
                return getWorkerDynamic("lua", "lua", "basic-languages");
            case Language.Markdown:
                return getWorkerDynamic(
                    "markdown",
                    "markdown",
                    "basic-languages"
                );
            case Language.ObjectiveC:
                return getWorkerDynamic(
                    "objective-c",
                    "objective-c",
                    "basic-languages"
                );
            case Language.Pascal:
                return getWorkerDynamic("pascal", "pascal", "basic-languages");
            case Language.Perl:
                return getWorkerDynamic("perl", "perl", "basic-languages");
            case Language.Php:
                return getWorkerDynamic("php", "php", "basic-languages");
            case Language.Powershell:
                return getWorkerDynamic(
                    "powershell",
                    "powershell",
                    "basic-languages"
                );
            case Language.Protobuf:
                return getWorkerDynamic(
                    "protobuf",
                    "protobuf",
                    "basic-languages"
                );
            case Language.Pug:
                return getWorkerDynamic("pug", "pug", "basic-languages");
            case Language.Python:
                return getWorkerDynamic("python", "python", "basic-languages");
            case Language.R:
                return getWorkerDynamic("r", "r", "basic-languages");
            case Language.Razor:
                return getWorkerDynamic("razor", "razor", "basic-languages");
            case Language.Ruby:
                return getWorkerDynamic("ruby", "ruby", "basic-languages");
            case Language.Scala:
                return getWorkerDynamic("scala", "scala", "basic-languages");
            case Language.Sass:
                return getWorkerDynamic("scss", "scss", "basic-languages");
            case Language.Shell:
                return getWorkerDynamic("shell", "shell", "basic-languages");
            case Language.Sql:
                return getWorkerDynamic("sql", "sql", "basic-languages");
            case Language.Swift:
                return getWorkerDynamic("swift", "swift", "basic-languages");
            case Language.Vb:
                return getWorkerDynamic("vb", "vb", "basic-languages");
            case Language.Xml:
                return getWorkerDynamic("xml", "xml", "basic-languages");
            case Language.Yaml:
                return getWorkerDynamic("yaml", "yaml", "basic-languages");
            default:
                return new editorWorker();
        }
    },
};

loader.config({ monaco });

export const FileEditor = ({ height, path }: FileEditorProps) => {
    const { isLoaded, content, setContent } = useFile(path);

    const language = useMemo(() => {
        if (path.indexOf(".") === -1) return "plaintext";

        const fileExtension = path.split(".").pop()?.toLowerCase();

        switch (fileExtension) {
            case "py":
                return Language.Python;
            case "js":
            case "mjs":
            case "cjs":
            case "ts":
                return Language.Typescript;
            case "html":
            case "htm":
                return Language.Html;
            case "css":
                return Language.Css;
            case "md":
            case "markdown":
                return Language.Markdown;
            case "rs":
                return Language.Rust;
            case "coffee":
                return Language.Coffee;
            case "bat":
            case "cmd":
                return Language.Bat;
            case "bicep":
                return Language.Bicep;
            case "clojure":
            case "clj":
            case "cljc":
            case "cljs":
                return Language.Clojure;
            case "cpp":
            case "h":
            case "hpp":
            case "cc":
            case "cxx":
                return Language.Cpp;
            case "cs":
                return Language.Csharp;
            case "dart":
                return Language.Dart;
            case "dockerfile":
            case "docker":
                return Language.Dockerfile;
            case "ex":
            case "exs":
                return Language.Elixir;
            case "fs":
            case "fsx":
            case "fsi":
                return Language.Fsharp;
            case "go":
                return Language.Go;
            case "graphql":
            case "gql":
                return Language.Graphql;
            case "hbs":
            case "handlebars":
                return Language.Handlebars;
            case "ini":
                return Language.Ini;
            case "java":
                return Language.Java;
            case "kt":
            case "kts":
                return Language.Kotlin;
            case "less":
                return Language.Less;
            case "lua":
                return Language.Lua;
            case "m":
                return Language.ObjectiveC;
            case "p":
                return Language.Pascal;
            case "pl":
            case "pm":
                return Language.Perl;
            case "php":
                return Language.Php;
            case "ps1":
            case "psm1":
                return Language.Powershell;
            case "proto":
                return Language.Protobuf;
            case "pug":
            case "jade":
                return Language.Pug;
            case "r":
                return Language.R;
            case "rb":
                return Language.Ruby;
            case "scala":
                return Language.Scala;
            case "scss":
            case "sass":
                return Language.Sass;
            case "sh":
                return Language.Shell;
            case "sql":
                return Language.Sql;
            case "swift":
                return Language.Swift;
            case "vb":
                return Language.Vb;
            case "xml":
            case "xsl":
            case "xslt":
                return Language.Xml;
            case "yaml":
            case "yml":
                return Language.Yaml;
            default:
                return "plaintext";
        }
    }, [path]);

    return (
        <Editor
            height={height}
            theme="vs-dark"
            defaultLanguage={language}
            value={content}
            onChange={(evt) => setContent(evt || "")}
        />
    );
};
