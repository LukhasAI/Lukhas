import assert from "node:assert";
import test from "node:test";
import { Lukhas } from "./index.js";

test("auditViewUrl formats", () => {
  const c = new Lukhas({ baseUrl: "http://x" });
  assert.equal(c.auditViewUrl("A-1"), "http://x/audit/view/A-1");
});
