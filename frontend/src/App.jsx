import { useState } from "react";
import { runScenario } from "./api";

export default function App() {
  const [scenario, setScenario] = useState("Generate 5 overdue invoices for a US vendor in Concur");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await runScenario(scenario);
      setResult(data);
    } catch (err) {
      setError(err.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <header className="header">
        <h1>Enterprise A2A Platform</h1>
        <p>Event-driven multi-agent automation for SAP Concur</p>
      </header>

      <main className="card">
        <form onSubmit={onSubmit}>
          <label>Business Scenario</label>
          <textarea
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
            rows={4}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Running..." : "Run Scenario"}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {result && (
          <div className="result">
            <h3>Result</h3>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </main>
    </div>
  );
}
