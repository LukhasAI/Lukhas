

// 📂 FILE: login.js
// 🔐 PURPOSE: Symbolic LucasID login screen

import { useState } from "react";
import ParticleMorpher from "./ParticleMorpher";

const [username, setUsername] = useState("");
const [seed, setSeed] = useState("");
const [status, setStatus] = useState("");
const [ritualActive, setRitualActive] = useState(false);

const handleLogin = async () => {
  setRitualActive(true);
  setStatus("🔐 Verifying symbolic credentials...");
  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, seed }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Login failed");
    setStatus(`✅ Login success — welcome, ${username}`);
  } catch (err) {
    setStatus(`❌ ${err.message}`);
  }
  setTimeout(() => setRitualActive(false), 1800);
};

return (
  <div style={{ padding: "2em", fontFamily: "sans-serif", maxWidth: "600px", margin: "auto" }}>
    <h2>🔑 LucasID Login</h2>
    <p>Enter your symbolic identity to access the mesh:</p>

    <label>
      Username Slug:
      <input
        type="text"
        value={username}
        onChange={e => setUsername(e.target.value)}
        placeholder="e.g. alicesmith"
        style={{ width: "100%", padding: "0.5em", marginTop: "0.5em" }}
      />
    </label>
    <br /><br />

    <label>
      Seed Phrase:
      <input
        type="password"
        value={seed}
        onChange={e => setSeed(e.target.value)}
        placeholder="e.g. dream moon olive 🔮"
        style={{ width: "100%", padding: "0.5em", marginTop: "0.5em" }}
      />
    </label>
    <br /><br />

    <button onClick={handleLogin} style={{ padding: "0.75em 1.5em" }}>
      🧬 Authenticate
    </button>

    <ParticleMorpher trigger={ritualActive} />
    <p style={{ marginTop: "1em", color: "#666" }}>{status}</p>
  </div>
);
}
