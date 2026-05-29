import assert from "node:assert/strict";
import test from "node:test";
import { resolvePythonCommand, toolResponse } from "../src/cliBridge.js";

test("toolResponse marks failed CLI result as MCP error", () => {
  const response = toolResponse({ ok: false, exitCode: 2, stdout: "", stderr: "blocked" });
  assert.equal(response.isError, true);
  assert.match(response.content[0].text, /blocked|exitCode/);
});

test("resolvePythonCommand ignores PYTHON because it may point to Python 2", () => {
  assert.equal(resolvePythonCommand({ PYTHON: "python2" }), "python3");
  assert.equal(resolvePythonCommand({ PYTHON: "python2", ROBOT_TESTKIT_PYTHON: "/opt/ros/bin/python3" }), "/opt/ros/bin/python3");
});
