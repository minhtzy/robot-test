import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import express from "express";
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";
import { shouldRunAsync } from "./asyncOptions.js";
import { repoRoot, runRobotCli, toolResponse } from "./cliBridge.js";
import { cancelJob, getJobStatus, readJobLogs, startRobotCliJob } from "./jobManager.js";

const CommonOptions = {
  config: z.string().optional(),
  dryRun: z.boolean().default(false),
  asyncRun: z.boolean().optional()
};

async function runCliTool(args: string[], options: { config?: string; dryRun?: boolean; asyncRun?: boolean; label?: string; defaultAsync?: boolean }) {
  if (shouldRunAsync(options.asyncRun, options.defaultAsync)) {
    return toolResponse({ ok: true, exitCode: 0, stdout: "", stderr: "", json: await startRobotCliJob(args, options) });
  }
  return toolResponse(await runRobotCli(args, options));
}

function createServer(): McpServer {
  const server = new McpServer({ name: "robot-testkit", version: "0.1.0" });

  server.registerTool("build_source", {
    description: "Run colcon build for the ROS2 workspace.",
    inputSchema: { ...CommonOptions, profile: z.string().optional() }
  }, async ({ config, dryRun, asyncRun, profile }) => {
    const args = ["build"];
    if (profile) args.push("--profile", profile);
    return runCliTool(args, { config, dryRun, asyncRun, label: "build", defaultAsync: true });
  });

  server.registerTool("run_lint_tests", {
    description: "Run colcon test with lint options from config.",
    inputSchema: { ...CommonOptions, profile: z.string().optional() }
  }, async ({ config, dryRun, asyncRun, profile }) => {
    const args = ["lint"];
    if (profile) args.push("--profile", profile);
    return runCliTool(args, { config, dryRun, asyncRun, label: "lint", defaultAsync: true });
  });

  server.registerTool("targets", {
    description: "Return configured build packages, lint packages, ROS2 nodes, services, and topics for a robot profile.",
    inputSchema: { ...CommonOptions, profile: z.string() }
  }, async ({ config, dryRun, profile }) => toolResponse(await runRobotCli(["targets", "--profile", profile], { config, dryRun })));

  server.registerTool("launch_target", {
    description: "Launch simulation, attach to a real robot, or call the FANUC Windows bridge.",
    inputSchema: { ...CommonOptions, profile: z.string() }
  }, async ({ config, dryRun, asyncRun, profile }) => runCliTool(["launch", "--profile", profile], { config, dryRun, asyncRun, label: "launch", defaultAsync: true }));

  server.registerTool("browser_login", {
    description: "Open robot browser login using VS Code browser tool, Playwright, or system browser fallback.",
    inputSchema: { ...CommonOptions, profile: z.string().optional() }
  }, async ({ config, dryRun, asyncRun }) => runCliTool(["browser-login"], { config, dryRun, asyncRun, label: "browser-login", defaultAsync: true }));

  server.registerTool("start_nodes", {
    description: "Start configured ROS2 nodes with ros2 run.",
    inputSchema: { ...CommonOptions, profile: z.string(), nodes: z.array(z.string()).optional() }
  }, async ({ config, dryRun, asyncRun, profile, nodes }) => {
    const args = ["start-nodes", "--profile", profile];
    for (const node of nodes ?? []) args.push("--node", node);
    return runCliTool(args, { config, dryRun, asyncRun, label: "start-nodes", defaultAsync: true });
  });

  server.registerTool("call_service", {
    description: "Call an allowlisted ROS2 service. Physical robot actions require confirm=true.",
    inputSchema: {
      ...CommonOptions,
      profile: z.string(),
      service: z.string(),
      serviceType: z.string().optional(),
      payload: z.string().optional(),
      confirm: z.boolean().default(false)
    }
  }, async ({ config, dryRun, asyncRun, profile, service, serviceType, payload, confirm }) => {
    const args = ["call-service", "--profile", profile, "--service", service];
    if (serviceType !== undefined) args.push("--type", serviceType);
    if (payload !== undefined) args.push("--payload", payload);
    if (confirm) args.push("--confirm");
    return runCliTool(args, { config, dryRun, asyncRun, label: "service", defaultAsync: true });
  });

  server.registerTool("monitor_topic", {
    description: "Monitor a ROS2 topic for a bounded duration.",
    inputSchema: { ...CommonOptions, profile: z.string().optional(), topic: z.string(), seconds: z.number().int().positive().default(10) }
  }, async ({ config, dryRun, asyncRun, profile, topic, seconds }) => {
    const args = ["monitor-topic", "--topic", topic, "--seconds", String(seconds)];
    if (profile) args.push("--profile", profile);
    return runCliTool(args, { config, dryRun, asyncRun, label: "topic", defaultAsync: true });
  });

  server.registerTool("collect_logs", {
    description: "Collect and analyze latest logs into reports/latest.json.",
    inputSchema: CommonOptions
  }, async ({ config, dryRun, asyncRun }) => runCliTool(["collect-logs"], { config, dryRun, asyncRun, label: "collect-logs", defaultAsync: true }));

  server.registerTool("analyze_run", {
    description: "Analyze latest run logs and return pass/fail findings.",
    inputSchema: CommonOptions
  }, async ({ config, dryRun, asyncRun }) => runCliTool(["analyze"], { config, dryRun, asyncRun, label: "analyze", defaultAsync: true }));

  server.registerTool("run_scenario", {
    description: "Run build, lint, launch, browser login, nodes, topic monitor, analysis, and memory update.",
    inputSchema: { ...CommonOptions, profile: z.string(), confirm: z.boolean().default(false), monitorSeconds: z.number().int().positive().default(10) }
  }, async ({ config, dryRun, asyncRun, profile, confirm, monitorSeconds }) => {
    const args = ["run-scenario", "--profile", profile, "--monitor-seconds", String(monitorSeconds)];
    if (confirm) args.push("--confirm");
    return runCliTool(args, { config, dryRun, asyncRun, label: "scenario", defaultAsync: true });
  });

  server.registerTool("update_memory", {
    description: "Persist the latest analyzed run outcome to local memory.",
    inputSchema: { ...CommonOptions, profile: z.string() }
  }, async ({ config, dryRun, asyncRun, profile }) => runCliTool(["update-memory", "--profile", profile], { config, dryRun, asyncRun, label: "memory", defaultAsync: true }));

  server.registerTool("job_status", {
    description: "Return status for an async robot test job.",
    inputSchema: { runId: z.string() }
  }, async ({ runId }) => toolResponse({ ok: true, exitCode: 0, stdout: "", stderr: "", json: await getJobStatus(runId) }));

  server.registerTool("job_logs", {
    description: "Return recent log lines for an async robot test job.",
    inputSchema: { runId: z.string(), tailLines: z.number().int().positive().default(80) }
  }, async ({ runId, tailLines }) => toolResponse({ ok: true, exitCode: 0, stdout: "", stderr: "", json: await readJobLogs(runId, tailLines) }));

  server.registerTool("job_cancel", {
    description: "Cancel a running async robot test job.",
    inputSchema: { runId: z.string() }
  }, async ({ runId }) => toolResponse({ ok: true, exitCode: 0, stdout: "", stderr: "", json: await cancelJob(runId) }));

  server.registerResource("robot-profiles", "robot://profiles", {
    description: "Robot profiles from config/robot-testkit.yaml",
    mimeType: "text/yaml"
  }, async (uri) => readTextResource(uri.href, "config/robot-testkit.yaml"));

  server.registerResource("robot-latest-report", "robot://reports/latest", {
    description: "Latest analysis report.",
    mimeType: "application/json"
  }, async (uri) => readTextResource(uri.href, "reports/latest.json"));

  server.registerResource("robot-memory-lessons", "robot://memory/lessons", {
    description: "Local lessons learned memory.",
    mimeType: "application/jsonl"
  }, async (uri) => readTextResource(uri.href, ".robot-test-memory/lessons.jsonl"));

  server.registerResource("robot-latest-run", "robot://runs/latest", {
    description: "Local run history memory.",
    mimeType: "application/jsonl"
  }, async (uri) => readTextResource(uri.href, ".robot-test-memory/runs.jsonl"));

  server.registerResource("robot-scenarios", new ResourceTemplate("robot://scenarios/{profile}", { list: undefined }), {
    description: "Scenario summary for a robot profile.",
    mimeType: "application/json"
  }, async (uri, variables) => ({
    contents: [{ uri: uri.href, mimeType: "application/json", text: JSON.stringify({ profile: variables.profile, workflow: ["build", "lint", "launch", "browser_login", "start_nodes", "monitor_topics", "analyze", "update_memory"] }, null, 2) }]
  }));

  server.registerPrompt("plan_robot_test", {
    description: "Plan a safe robot test run.",
    argsSchema: { profile: z.string() }
  }, ({ profile }) => ({
    messages: [{ role: "user", content: { type: "text", text: `Plan a safe test run for robot profile ${profile}. Build and lint must pass before launch. Confirm before physical actions.` } }]
  }));

  server.registerPrompt("analyze_robot_failure", {
    description: "Analyze robot test logs and propose fixes.",
    argsSchema: { profile: z.string().optional() }
  }, ({ profile }) => ({
    messages: [{ role: "user", content: { type: "text", text: `Analyze latest robot test failure${profile ? ` for ${profile}` : ""}. Use logs, report, and local lessons. Do not expose secrets.` } }]
  }));

  server.registerPrompt("write_regression_scenario", {
    description: "Write a regression scenario from a known failure.",
    argsSchema: { failureSignature: z.string() }
  }, ({ failureSignature }) => ({
    messages: [{ role: "user", content: { type: "text", text: `Create a regression scenario for failure signature: ${failureSignature}` } }]
  }));

  return server;
}

async function readTextResource(uri: string, relativePath: string) {
  const absolute = path.join(repoRoot(), relativePath);
  let text = "";
  try {
    text = await fs.readFile(absolute, "utf8");
  } catch {
    text = "";
  }
  return { contents: [{ uri, text }] };
}

async function startStdio() {
  const server = createServer();
  await server.connect(new StdioServerTransport());
}

async function startHttp(port: number) {
  const app = express();
  app.use(express.json({ limit: "2mb" }));

  app.all("/mcp", async (req, res) => {
    const server = createServer();
    const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: () => crypto.randomUUID() });
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  });

  const sseTransports = new Map<string, SSEServerTransport>();
  app.get("/sse", async (_req, res) => {
    const server = createServer();
    const transport = new SSEServerTransport("/messages", res);
    sseTransports.set(transport.sessionId, transport);
    res.on("close", () => sseTransports.delete(transport.sessionId));
    await server.connect(transport);
  });
  app.post("/messages", async (req, res) => {
    const sessionId = String(req.query.sessionId || "");
    const transport = sseTransports.get(sessionId);
    if (!transport) {
      res.status(404).send("unknown SSE session");
      return;
    }
    await transport.handlePostMessage(req, res, req.body);
  });

  app.listen(port, () => {
    console.error(`robot-testkit MCP listening on http://127.0.0.1:${port}/mcp`);
  });
}

const args = process.argv.slice(2);
const transportIndex = args.indexOf("--transport");
const transport = transportIndex >= 0 ? args[transportIndex + 1] : "stdio";
const portIndex = args.indexOf("--port");
const port = portIndex >= 0 ? Number(args[portIndex + 1]) : 3333;

if (transport === "stdio") {
  await startStdio();
} else if (transport === "http") {
  await startHttp(port);
} else {
  throw new Error(`unsupported transport: ${transport}`);
}
