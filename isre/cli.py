"""Command-line interface for ISRE."""

import argparse
import json
import logging
import sys

from .pipeline import ISREPipeline
from .utils.logging import set_level


def main():
    parser = argparse.ArgumentParser(
        prog="isre",
        description="Intentional Semantic Reasoning Engine - A deterministic, 5-layer semantic reasoning system",
    )
    parser.add_argument("input", nargs="?", help="Input text to process")
    parser.add_argument("-m", "--modality", default="text", help="Input modality (default: text)")
    parser.add_argument("-f", "--format", nargs="+", help="Output formats (default: text code action markdown)")
    parser.add_argument("--trace", action="store_true", help="Show processing trace")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    args = parser.parse_args()

    if args.verbose:
        set_level(logging.DEBUG)

    if not args.input:
        if sys.stdin.isatty():
            parser.print_help()
            sys.exit(1)
        args.input = sys.stdin.read().strip()

    pipeline = ISREPipeline()
    formats = args.format or ["text", "code", "action", "markdown"]

    try:
        result = pipeline.process(args.input, args.modality, formats)

        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"Input: {args.input}")
            print("-" * 50)
            for fmt, output in result["outputs"].items():
                print(f"\n[{fmt.upper()}]")
                print(output)
            if result.get("knowledge_gaps"):
                print(f"\nKnowledge gaps: {result['knowledge_gaps']}")
            print(f"\nConfidence: {result['decision_metadata']['confidence']:.2f}")

            if args.trace:
                print("\n" + "=" * 50)
                print("TRACE:")
                for entry in pipeline.get_trace(result["request_id"]):
                    print(f"  [{entry['stage']}] {json.dumps(entry['data'], default=str)[:100]}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
