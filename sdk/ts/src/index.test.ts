import assert from "node:assert";
import test from "node:test";
import { LukhasPWM } from "./index.js";

test("auditViewUrl formats", () => {
  const c = new LukhasPWM({ baseUrl: "http://x" });
  assert.equal(c.auditViewUrl("A-1"), "http://x/audit/view/A-1");
});
