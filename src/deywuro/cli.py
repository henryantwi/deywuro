"""Command-line interface for the Deywuro SMS client."""

import argparse
import json
import os
import sys

from .client import DeywuroClient
from .exceptions import DeywuroError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="deywuro", description="Deywuro SMS client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    send_parser = subparsers.add_parser("send", help="Send an SMS")
    send_parser.add_argument(
        "--to", required=True, help="Destination number(s), comma-separated"
    )
    send_parser.add_argument("--message", required=True, help="SMS body")
    send_parser.add_argument(
        "--username",
        default=os.environ.get("DEYWURO_USERNAME"),
        help="Deywuro username",
    )
    send_parser.add_argument(
        "--password",
        default=os.environ.get("DEYWURO_PASSWORD"),
        help="Deywuro password",
    )
    send_parser.add_argument(
        "--source", default=os.environ.get("DEYWURO_SOURCE"), help="Sender ID"
    )
    send_parser.add_argument(
        "--method", default="GET", choices=["GET", "POST"], help="HTTP method"
    )
    send_parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip Ghanaian number validation/normalization",
    )

    return parser


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "send":
        missing = [
            name
            for name, value in (
                ("--username", args.username),
                ("--password", args.password),
                ("--source", args.source),
            )
            if not value
        ]
        if missing:
            print(
                f"Missing required credentials: {', '.join(missing)} "
                "(pass as flags or set DEYWURO_USERNAME/DEYWURO_PASSWORD/DEYWURO_SOURCE)",
                file=sys.stderr,
            )
            return 1

        client = DeywuroClient(
            username=args.username, password=args.password, source=args.source
        )
        try:
            result = client.send(
                args.to,
                args.message,
                method=args.method,
                validate=not args.no_validate,
            )
        except DeywuroError as exc:
            print(json.dumps({"error": exc.message, "code": exc.code}), file=sys.stderr)
            return 1

        print(json.dumps({"code": result.code, "message": result.message}))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
