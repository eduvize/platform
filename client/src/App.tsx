import "./App.css";
import { AuthProvider } from "./context";
import { Dashboard, Router } from "./views";

function App() {
    return (
        <AuthProvider>
            <Router />
        </AuthProvider>
    );
}

export default App;
