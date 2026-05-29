import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import { spawn } from "node:child_process";
import { repoRoot, resolvePythonCommand } from "./cliBridge.js";

export type JobRecord = {
  runId: string;
  pid?: number;
  status: "running" | "completed" | "failed" | "cancelled";
  command: string[];
  startedAt: string;
  finishedAt?: string;
  exitCode?: number | null;
  logPath: string;
  metadataPath: string;
};

function jobsRoot(): string {
  return path.join(repoRoot(), ".robot-test-memory", "jobs");
}

function jobLogRoot(): string {
  return path.join(repoRoot(), "logs", "jobs");
}

function nowId(): string {
  const stamp = new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14);
  const suffix = Math.random().toString(36).slice(2, 8);
  return `${stamp}-${suffix}`;
}

async function ensureDirs() {
  await fsp.mkdir(jobsRoot(), { recursive: true });
  await fsp.mkdir(jobLogRoot(), { recursive: true });
}

async function writeRecord(record: JobRecord) {
  await fsp.writeFile(record.metadataPath, JSON.stringify(record, null, 2), "utf8");
}

async function readRecord(runId: string): Promise<JobRecord> {
  const metadataPath = path.join(jobsRoot(), `${runId}.json`);
  return JSON.parse(await fsp.readFile(metadataPath, "utf8")) as JobRecord;
}

export async function startRobotCliJob(args: string[], options: { config?: string; dryRun?: boolean; label?: string } = {}) {
  await ensureDirs();
  const root = repoRoot();
  const python = await resolvePythonCommand();
  const runId = `${options.label ?? "robot"}-${nowId()}`;
  const metadataPath = path.join(jobsRoot(), `${runId}.json`);
  const logPath = path.join(jobLogRoot(), `${runId}.log`);
  const cliArgs = ["-m", "robot_testkit.cli"];
  if (options.config) cliArgs.push("--config", options.config);
  if (options.dryRun) cliArgs.push("--dry-run");
  cliArgs.push(...args);

  const command = [python, ...cliArgs];
  const record: JobRecord = {
    runId,
    status: "running",
    command,
    startedAt: new Date().toISOString(),
    logPath,
    metadataPath
  };
  await writeRecord(record);

  const out = fs.openSync(logPath, "a");
  fs.writeSync(out, `$ ${command.map(shellQuote).join(" ")}\n`);
  const child = spawn(python, cliArgs, {
    cwd: root,
    detached: true,
    stdio: ["ignore", out, out],
    env: process.env
  });
  record.pid = child.pid;
  await writeRecord(record);
  child.on("error", async (error) => {
    fs.writeSync(out, `\n[start error] ${error.message}\n`);
    fs.closeSync(out);
    await writeRecord({ ...record, status: "failed", exitCode: null, finishedAt: new Date().toISOString() });
  });
  child.on("close", async (exitCode) => {
    fs.writeSync(out, `\n[exit] code=${exitCode}\n`);
    fs.closeSync(out);
    await writeRecord({ ...record, status: exitCode === 0 ? "completed" : "failed", exitCode, finishedAt: new Date().toISOString() });
  });
  child.unref();

  return {
    runId,
    status: "running",
    pid: child.pid,
    command: command.join(" "),
    logPath,
    metadataPath,
    message: `Started ${args[0]} as job ${runId}. Use job_status and job_logs to monitor progress.`
  };
}

export async function getJobStatus(runId: string) {
  const record = await readRecord(runId);
  if (record.status === "running" && record.pid && !processExists(record.pid)) {
    const updated: JobRecord = { ...record, status: "failed", finishedAt: new Date().toISOString(), exitCode: null };
    await writeRecord(updated);
    return updated;
  }
  return record;
}

export async function readJobLogs(runId: string, tailLines = 80) {
  const record = await getJobStatus(runId);
  let log = "";
  try {
    log = await fsp.readFile(record.logPath, "utf8");
  } catch {
    log = "";
  }
  const lines = log.split(/\r?\n/);
  return {
    ...record,
    tailLines,
    log: lines.slice(Math.max(0, lines.length - tailLines)).join("\n")
  };
}

export async function cancelJob(runId: string) {
  const record = await readRecord(runId);
  if (record.status !== "running") {
    return record;
  }
  if (record.pid) {
    try {
      process.kill(-record.pid, "SIGTERM");
    } catch {
      try {
        process.kill(record.pid, "SIGTERM");
      } catch {
        // The process may have exited between status check and cancellation.
      }
    }
  }
  const updated: JobRecord = { ...record, status: "cancelled", finishedAt: new Date().toISOString(), exitCode: null };
  await writeRecord(updated);
  return updated;
}

function processExists(pid: number) {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function shellQuote(value: string) {
  return /^[A-Za-z0-9_./:=+-]+$/.test(value) ? value : `'${value.replace(/'/g, "'\"'\"'")}'`;
}
