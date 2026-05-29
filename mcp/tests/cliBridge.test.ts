import assert from "node:assert/strict";
import test from "node:test";
import { isPython3Version, resolvePythonCommand, toolResponse } from "../src/cliBridge.js";
import { startRobotCliJob, readJobLogs } from "../src/jobManager.js";

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

test("startRobotCliJob returns a run id and writes logs", async () => {
  const job = await startRobotCliJob(["targets", "--profile", "fairino_sim"], { dryRun: true, label: "test" });
  assert.match(job.runId, /^test-/);
  for (let attempt = 0; attempt < 20; attempt++) {
    const logs = await readJobLogs(job.runId, 200);
    if (logs.status !== "running") {
      assert.match(logs.log, /fairino_sim|targets/);
      return;
    }
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
  throw new Error("job did not complete");
});
