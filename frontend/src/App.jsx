import React from "react";

function App() {
  return (
    <div style={{ fontFamily: "sans-serif", padding: "2rem", textAlign: "center" }}>
      <h1>📧 Email Reply Agent</h1>
      <p style={{ color: "#666" }}>
        Dashboard coming in Phase 6
      </p>
      <div style={{ marginTop: "2rem" }}>
        <a
          href="http://localhost:8000/docs"
          target="_blank"
          rel="noreferrer"
          style={{ marginRight: "1rem", color: "#0078d4" }}
        >
          → API Docs
        </a>
        <a
          href="http://localhost:8000/health"
          target="_blank"
          rel="noreferrer"
          style={{ color: "#0078d4" }}
        >
          → Health Check
        </a>
      </div>
    </div>
  );
}

export default App;