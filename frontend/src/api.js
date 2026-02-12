export async function runScenario(scenario) {
  const res = await fetch(import.meta.env.VITE_ORCHESTRATOR_URL || "http://localhost:8081/run-scenario", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario })
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Request failed");
  }

  return res.json();
}
