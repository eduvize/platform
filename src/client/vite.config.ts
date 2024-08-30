import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import path from "path";

export default defineConfig(() => {
    return {
        build: {
            outDir: "build",
        },
        plugins: [react(), tsconfigPaths()],
        server: {},
        resolve: {
            alias: {
                "@contracts": path.resolve(__dirname, "./src/api/contracts"),
                "@context": path.resolve(__dirname, "./src/context"),
                "@models": path.resolve(__dirname, "./src/models"),
                "@api": path.resolve(__dirname, "./src/api"),
                "@atoms": path.resolve(__dirname, "./src/components/atoms"),
                "@molecules": path.resolve(
                    __dirname,
                    "./src/components/molecules"
                ),
                "@organisms": path.resolve(
                    __dirname,
                    "./src/components/organisms"
                ),
                "@views": path.resolve(__dirname, "./src/views"),
                "@util": path.resolve(__dirname, "./src/util"),
            },
        },
    };
});
