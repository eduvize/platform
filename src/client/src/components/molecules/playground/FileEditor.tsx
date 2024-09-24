import { useFile } from "@context/playground/hooks";
import Editor from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import { loader } from "@monaco-editor/react";
import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import jsonWorker from "monaco-editor/esm/vs/language/json/json.worker?worker";
import cssWorker from "monaco-editor/esm/vs/language/css/css.worker?worker";
import htmlWorker from "monaco-editor/esm/vs/language/html/html.worker?worker";
import tsWorker from "monaco-editor/esm/vs/language/typescript/ts.worker?worker";
import rustWorker from "monaco-editor/esm/vs/basic-languages/rust/rust.contribution?worker";
import coffeeWorker from "monaco-editor/esm/vs/basic-languages/coffee/coffee.contribution?worker";
import batWorker from "monaco-editor/esm/vs/basic-languages/bat/bat.contribution?worker";
import bicepWorker from "monaco-editor/esm/vs/basic-languages/bicep/bicep.contribution?worker";
import clojureWorker from "monaco-editor/esm/vs/basic-languages/clojure/clojure.contribution?worker";
import cppWorker from "monaco-editor/esm/vs/basic-languages/cpp/cpp.contribution?worker";
import csharpWorker from "monaco-editor/esm/vs/basic-languages/csharp/csharp.contribution?worker";
import dartWorker from "monaco-editor/esm/vs/basic-languages/dart/dart.contribution?worker";
import dockerfileWorker from "monaco-editor/esm/vs/basic-languages/dockerfile/dockerfile.contribution?worker";
import elixirWorker from "monaco-editor/esm/vs/basic-languages/elixir/elixir.contribution?worker";
import fsharpWorker from "monaco-editor/esm/vs/basic-languages/fsharp/fsharp.contribution?worker";
import goWorker from "monaco-editor/esm/vs/basic-languages/go/go.contribution?worker";
import graphqlWorker from "monaco-editor/esm/vs/basic-languages/graphql/graphql.contribution?worker";
import handlebarsWorker from "monaco-editor/esm/vs/basic-languages/handlebars/handlebars.contribution?worker";
import iniWorker from "monaco-editor/esm/vs/basic-languages/ini/ini.contribution?worker";
import javaWorker from "monaco-editor/esm/vs/basic-languages/java/java.contribution?worker";
import kotlinWorker from "monaco-editor/esm/vs/basic-languages/kotlin/kotlin.contribution?worker";
import lessWorker from "monaco-editor/esm/vs/basic-languages/less/less.contribution?worker";
import luaWorker from "monaco-editor/esm/vs/basic-languages/lua/lua.contribution?worker";
import markdownWorker from "monaco-editor/esm/vs/basic-languages/markdown/markdown.contribution?worker";
import objectiveCWorker from "monaco-editor/esm/vs/basic-languages/objective-c/objective-c.contribution?worker";
import pascalWorker from "monaco-editor/esm/vs/basic-languages/pascal/pascal.contribution?worker";
import perlWorker from "monaco-editor/esm/vs/basic-languages/perl/perl.contribution?worker";
import phpWorker from "monaco-editor/esm/vs/basic-languages/php/php.contribution?worker";
import powershellWorker from "monaco-editor/esm/vs/basic-languages/powershell/powershell.contribution?worker";
import protobufWorker from "monaco-editor/esm/vs/basic-languages/protobuf/protobuf.contribution?worker";
import pugWorker from "monaco-editor/esm/vs/basic-languages/pug/pug.contribution?worker";
import pythonWorker from "monaco-editor/esm/vs/basic-languages/python/python.contribution?worker";
import rWorker from "monaco-editor/esm/vs/basic-languages/r/r.contribution?worker";
import razorWorker from "monaco-editor/esm/vs/basic-languages/razor/razor.contribution?worker";
import rubyWorker from "monaco-editor/esm/vs/basic-languages/ruby/ruby.contribution?worker";
import scalaWorker from "monaco-editor/esm/vs/basic-languages/scala/scala.contribution?worker";
import sassWorker from "monaco-editor/esm/vs/basic-languages/scss/scss.contribution?worker";
import shellWorker from "monaco-editor/esm/vs/basic-languages/shell/shell.contribution?worker";
import sqlWorker from "monaco-editor/esm/vs/basic-languages/sql/sql.contribution?worker";
import swiftWorker from "monaco-editor/esm/vs/basic-languages/swift/swift.contribution?worker";
import vbWorker from "monaco-editor/esm/vs/basic-languages/vb/vb.contribution?worker";
import xmlWorker from "monaco-editor/esm/vs/basic-languages/xml/xml.contribution?worker";
import yamlWorker from "monaco-editor/esm/vs/basic-languages/yaml/yaml.contribution?worker";
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

self.MonacoEnvironment = {
    getWorker(_, label) {
        switch (label) {
            case Language.Json:
                return new jsonWorker();
            case Language.Css:
                return new cssWorker();
            case Language.Html:
                return new htmlWorker();
            case Language.Typescript:
                return new tsWorker();
            case Language.Rust:
                return new rustWorker();
            case Language.Coffee:
                return new coffeeWorker();
            case Language.Bat:
                return new batWorker();
            case Language.Bicep:
                return new bicepWorker();
            case Language.Clojure:
                return new clojureWorker();
            case Language.Cpp:
                return new cppWorker();
            case Language.Csharp:
                return new csharpWorker();
            case Language.Dart:
                return new dartWorker();
            case Language.Dockerfile:
                return new dockerfileWorker();
            case Language.Elixir:
                return new elixirWorker();
            case Language.Fsharp:
                return new fsharpWorker();
            case Language.Go:
                return new goWorker();
            case Language.Graphql:
                return new graphqlWorker();
            case Language.Handlebars:
                return new handlebarsWorker();
            case Language.Ini:
                return new iniWorker();
            case Language.Java:
                return new javaWorker();
            case Language.Kotlin:
                return new kotlinWorker();
            case Language.Less:
                return new lessWorker();
            case Language.Lua:
                return new luaWorker();
            case Language.Markdown:
                return new markdownWorker();
            case Language.ObjectiveC:
                return new objectiveCWorker();
            case Language.Pascal:
                return new pascalWorker();
            case Language.Perl:
                return new perlWorker();
            case Language.Php:
                return new phpWorker();
            case Language.Powershell:
                return new powershellWorker();
            case Language.Protobuf:
                return new protobufWorker();
            case Language.Pug:
                return new pugWorker();
            case Language.Python:
                return new pythonWorker();
            case Language.R:
                return new rWorker();
            case Language.Razor:
                return new razorWorker();
            case Language.Ruby:
                return new rubyWorker();
            case Language.Scala:
                return new scalaWorker();
            case Language.Sass:
                return new sassWorker();
            case Language.Shell:
                return new shellWorker();
            case Language.Sql:
                return new sqlWorker();
            case Language.Swift:
                return new swiftWorker();
            case Language.Vb:
                return new vbWorker();
            case Language.Xml:
                return new xmlWorker();
            case Language.Yaml:
                return new yamlWorker();
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
