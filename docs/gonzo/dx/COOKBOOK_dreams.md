# 🍳 Cookbook — Dreams API

## cURL

```bash
curl -sS -H "Authorization: Bearer sk-test" -H "Content-Type: application/json" \
  -d '{"model":"lukhas","seed":"a serene lake","constraints":{"style":"surreal"}}' \
  http://localhost:8000/v1/dreams | jq .
```

## TypeScript

```ts
import axios from "axios";
const r = await axios.post("http://localhost:8000/v1/dreams", {
  model: "lukhas", seed: "a serene lake", constraints: { style: "surreal" }
}, { headers: { Authorization: "Bearer sk-test" }});
console.log(r.data);
```

## Notes

* Returns OpenAI-style envelope with `id`, `model`, `seed`, `traces`, `constraints`.
* Respects Guardian scopes; in dev `LUKHAS_POLICY_MODE=permissive` is simplest.
