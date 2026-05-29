import assert from "node:assert/strict";
import test from "node:test";
import { isPython3Version, resolvePythonCommand, toolResponse } from "../src/cliBridge.js";

test("toolResponse marks failed CLI result as MCP error", () => {
  const response = toolResponse({ ok: false, exitCode: 2, stdout: "", stderr: "blocked" });
  assert.equal(response.isError, true);
  assert.match(response.content[0].text, /blocked|exitCode/);
});

test("isPython3Version rejects Python 2 output", () => {
  assert.equal(isPython3Version("Python 2.7.18"), false);
  assert.equal(isPython3Version("Python 3.8.10"), true);
});

test("resolvePythonCommand ignores PYTHON because it may point to Python 2", async () => {
  assert.equal(await resolvePythonCommand({ PYTHON: "python2" }), "python3");
});
