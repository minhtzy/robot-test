import { spawn } from "node:child_process";
import path from "node:path";

export type CliResult = {
  ok: boolean;
  exitCode: number | null;
  stdout: string;
  stderr: string;
  json?: unknown;
};

export type RobotToolOptions = {
  config?: string;
  dryRun?: boolean;
};

export function repoRoot(): string {
  return path.resolve(path.dirname(new URL(import.meta.url).pathname), "..", "..", "..");
}

export async function runRobotCli(args: string[], options: RobotToolOptions = {}): Promise<CliResult> {
  const root = repoRoot();
  const python = process.env.ROBOT_TESTKIT_PYTHON || process.env.PYTHON || "python3";
  const cliArgs = ["-m", "robot_testkit.cli"];
  if (options.config) {
    cliArgs.push("--config", options.config);
  }
  if (options.dryRun) {
    cliArgs.push("--dry-run");
  }
  cliArgs.push(...args);

  return new Promise((resolve) => {
    const child = spawn(python, cliArgs, {
      cwd: root,
      stdio: ["ignore", "pipe", "pipe"],
      env: process.env
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("close", (exitCode) => {
      let parsed: unknown;
      try {
        parsed = stdout.trim() ? JSON.parse(stdout) : undefined;
      } catch {
        parsed = undefined;
      }
      resolve({ ok: exitCode === 0, exitCode, stdout, stderr, json: parsed });
    });
  });
}

export function toolResponse(result: CliResult) {
  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(result.json ?? { stdout: result.stdout, stderr: result.stderr, exitCode: result.exitCode }, null, 2)
      }
    ],
    isError: !result.ok
  };
}
