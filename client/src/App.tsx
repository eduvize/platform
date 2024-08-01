import { createTheme, MantineProvider } from "@mantine/core";
import "./App.css";
import { AuthProvider } from "./context";
import { Dashboard, Router } from "./views";
import "@mantine/core/styles.css";

function EduvizeApp() {
    const theme = createTheme({});

    return (
        <MantineProvider theme={theme} defaultColorScheme="dark">
            <AuthProvider>
                <Router />
            </AuthProvider>
        </MantineProvider>
    );
}

export default EduvizeApp;
