import express from "express";
import cors from "cors";

const app = express();
app.use(cors({ origin: true, credentials: true }));
app.use(express.json());

let balance = 0;

// Wallet endpoints
app.get("/balance", (_req, res) => res.json({ currency: "LUK", amount: balance }));

app.post("/earn", (req, res) => {
  const amt = Number(req.body?.amount ?? 10);
  balance += amt;
  res.json({ currency: "LUK", amount: balance });
});

app.post("/spend", (req, res) => {
  const amt = Number(req.body?.amount ?? 10);
  if (balance < amt) return res.status(400).json({ error: "insufficient" });
  balance -= amt;
  res.json({ currency: "LUK", amount: balance });
});

// QRG endpoints
app.post("/issue", (_req, res) => {
  const traceId = `trace_${Math.random().toString(36).slice(2,8)}`;
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><rect width='100%' height='100%' fill='#0b0d12'/><circle cx='110' cy='110' r='80' stroke='#9bb3ff' stroke-width='2' fill='none'/><circle cx='110' cy='110' r='40' stroke='#9bb3ff' stroke-width='2' fill='none'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='#9bb3ff' font-size='10'>QRG·${traceId}</text></svg>`;
  res.json({ glyphSvg: svg, nonce: "dev-nonce", traceId });
});

// Identity endpoints
app.post("/signin/start", (_req, res) => {
  const challengeId = `challenge_${Math.random().toString(36).slice(2,8)}`;
  res.json({ challengeId });
});

// Consent endpoints
app.post("/record", (req, res) => {
  const { scope, granted } = req.body;
  res.json({
    userId: "dev-user",
    scope: scope || "unknown",
    granted: granted ?? true,
    timestamp: new Date().toISOString()
  });
});

app.get("/records", (_req, res) => {
  res.json([
    { userId: "dev-user", scope: "analytics", granted: false, timestamp: new Date().toISOString() },
    { userId: "dev-user", scope: "sponsors", granted: true, timestamp: new Date().toISOString() }
  ]);
});

const port = process.env.PORT || 7402;
app.listen(port, () => console.log(`dev-apis running on port ${port}`));
