const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 8080;

// Enable CORS for iframe embedding
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:3001', 'https://lukhas.ai', 'https://*.lukhas.ai'],
  credentials: true,
}));

// Serve static files from the current directory
app.use(express.static(path.join(__dirname)));

// Security headers for iframe embedding
app.use((req, res, next) => {
  // Allow embedding in same origin and LUKHAS domains
  res.setHeader('X-Frame-Options', 'SAMEORIGIN');
  res.setHeader('Content-Security-Policy', "frame-ancestors 'self' http://localhost:* https://*.lukhas.ai");
  next();
});

// Main route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'PR0T3US Voice-Reactive Morphing System' });
});

app.listen(PORT, () => {
  console.log(`PR0T3US server running on http://localhost:${PORT}`);
  console.log(`To integrate with LUKHAS website, ensure Next.js is configured to proxy /proteus to this server`);
});