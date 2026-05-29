from __future__ import annotations

import argparse
import json
import sys

from .config import load_config
from .errors import RobotTestkitError
from .orchestrator import RobotOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="robot-testkit")
    parser.add_argument("--config", default="config/robot-testkit.yaml")
    parser.add_argument("--dry-run", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("build")
    sub.add_parser("lint")

    launch = sub.add_parser("launch")
    launch.add_argument("--profile", required=True)

    login = sub.add_parser("browser-login")
    login.add_argument("--profile")

    nodes = sub.add_parser("start-nodes")
    nodes.add_argument("--profile", required=True)

    service = sub.add_parser("call-service")
    service.add_argument("--profile", required=True)
    service.add_argument("--service", required=True)
    service.add_argument("--type", required=True)
    service.add_argument("--payload", required=True)
    service.add_argument("--confirm", action="store_true")

    topic = sub.add_parser("monitor-topic")
    topic.add_argument("--topic", required=True)
    topic.add_argument("--seconds", type=int, default=10)

    sub.add_parser("collect-logs")
    sub.add_parser("analyze")

    scenario = sub.add_parser("run-scenario")
    scenario.add_argument("--profile", required=True)
    scenario.add_argument("--confirm", action="store_true")
    scenario.add_argument("--monitor-seconds", type=int, default=10)

    memory = sub.add_parser("update-memory")
    memory.add_argument("--profile", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        orchestrator = RobotOrchestrator(config, dry_run=args.dry_run)

        if args.command == "build":
            output = orchestrator.build_source().summary()
        elif args.command == "lint":
            output = orchestrator.run_lint_tests().summary()
        elif args.command == "launch":
            output = orchestrator.launch_target(config.profile(args.profile))
        elif args.command == "browser-login":
            output = orchestrator.login_browser()
        elif args.command == "start-nodes":
            output = orchestrator.start_nodes(config.profile(args.profile))
        elif args.command == "call-service":
            profile = config.profile(args.profile)
            output = orchestrator.call_service(profile, args.service, args.type, args.payload, confirmed=args.confirm).summary()
        elif args.command == "monitor-topic":
            output = orchestrator.monitor_topic(args.topic, duration_seconds=args.seconds).summary()
        elif args.command in {"collect-logs", "analyze"}:
            output = orchestrator.collect_logs()
        elif args.command == "run-scenario":
            output = orchestrator.run_scenario(args.profile, confirmed=args.confirm, monitor_seconds=args.monitor_seconds)
        elif args.command == "update-memory":
            profile = config.profile(args.profile)
            output = orchestrator.update_memory(profile, orchestrator.collect_logs())
        else:
            raise AssertionError(args.command)

        print(json.dumps(output, indent=2, ensure_ascii=False))
        return 0
    except RobotTestkitError as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

