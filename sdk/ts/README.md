# @lukhas/pwm — TypeScript SDK

## Install (local)
```bash
cd sdk/ts
npm i
npm run build
```

## Usage

```ts
import { LukhasPWM } from "@lukhas/pwm";

const client = new LukhasPWM({ baseUrl: "http://127.0.0.1:8000", apiKey: "dev-key" });

await client.feedbackCard({ target_action_id: "A-1", rating: 5, note: "great" });
const reg = await client.toolsRegistry();
const names = await client.toolsNames();
const health = await client.dnaHealth();

console.log(client.auditViewUrl("A-XYZ"));
```
