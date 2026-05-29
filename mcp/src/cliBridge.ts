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

function uniqueDefined(values: Array<string | undefined>): string[] {
  return Array.from(new Set(values.filter((value): value is string => Boolean(value))));
}

export function isPython3Version(output: string): boolean {
  return /^Python\s+3\./.test(output.trim());
}

async function readPythonVersion(command: string): Promise<string | null> {
  return new Promise((resolve) => {
    const child = spawn(command, ["--version"], { stdio: ["ignore", "pipe", "pipe"] });
    let output = "";
    child.stdout.on("data", (chunk) => {
      output += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      output += chunk.toString();
    });
    child.on("error", () => {
      resolve(null);
    });
    child.on("close", (exitCode) => {
      resolve(exitCode === 0 ? output : null);
    });
  });
}

export async function resolvePythonCommand(env: NodeJS.ProcessEnv = process.env): Promise<string> {
  const candidates = uniqueDefined([env.ROBOT_TESTKIT_PYTHON, "python3", "python"]);
  for (const candidate of candidates) {
    const version = await readPythonVersion(candidate);
    if (version && isPython3Version(version)) {
      return candidate;
    }
  }
  return "python3";
}

export async function runRobotCli(args: string[], options: RobotToolOptions = {}): Promise<CliResult> {
  const root = repoRoot();
  const python = await resolvePythonCommand();
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
    child.on("error", (error) => {
      resolve({
        ok: false,
        exitCode: null,
        stdout,
        stderr: `${stderr}${error.message}`,
        json: { status: "error", message: `failed to start Python 3 command '${python}': ${error.message}` }
      });
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
