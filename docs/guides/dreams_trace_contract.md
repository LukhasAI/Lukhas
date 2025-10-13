# Dreams Trace Contract (v1)
Fields: id, model, seed, constraints, steps[], duration_ms.
Each step: {type: "thought"|"action"|"observation", ts_ms, data:{} }.
Errors produce OpenAI-compatible envelopes; X-Trace-Id always set.
