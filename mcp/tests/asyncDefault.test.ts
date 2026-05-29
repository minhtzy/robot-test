import assert from "node:assert/strict";
import test from "node:test";
import { shouldRunAsync } from "../src/asyncOptions.js";

test("asyncRun defaults to async for long-running tools", () => {
  assert.equal(shouldRunAsync(undefined, true), true);
  assert.equal(shouldRunAsync(false, true), false);
  assert.equal(shouldRunAsync(true, false), true);
  assert.equal(shouldRunAsync(undefined, false), false);
});
