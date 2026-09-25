import { useEffect, useState } from "react";

export default function App() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then(setHealth)
      .catch((err) => setError(String(err)));
  }, []);

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", maxWidth: 640, margin: "3rem auto", padding: "0 1rem" }}>
      <h1>AI Assistant</h1>
      <p>Frontend React servido via nginx, conversando com o FastAPI em <code>/api</code>.</p>

      <h2>Status dos serviços</h2>
      {error && <pre style={{ color: "crimson" }}>{error}</pre>}
      {health ? (
        <pre style={{ background: "#f4f4f5", padding: "1rem", borderRadius: 8 }}>
          {JSON.stringify(health, null, 2)}
        </pre>
      ) : (
        !error && <p>Carregando…</p>
      )}
    </main>
  );
}
