import assert from "node:assert/strict";
import test from "node:test";
import { toolResponse } from "../src/cliBridge.js";

test("toolResponse marks failed CLI result as MCP error", () => {
  const response = toolResponse({ ok: false, exitCode: 2, stdout: "", stderr: "blocked" });
  assert.equal(response.isError, true);
  assert.match(response.content[0].text, /blocked|exitCode/);
});

