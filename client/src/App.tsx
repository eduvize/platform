import React, { useEffect, useRef } from "react";
import logo from "./logo.svg";
import { io, Socket } from "socket.io-client";
import "./App.css";

function App() {
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    socketRef.current = io("http://localhost:8000", {
      transports: ["websocket"],
      addTrailingSlash: true,
    });

    socketRef.current.on("connect", () => {
      console.log("Connected to server");
    });

    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.tsx</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
