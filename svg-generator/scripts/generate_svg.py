#!/usr/bin/env python3
"""
Generate SVG images from text prompts using the Quiver AI API.

Usage:
    python3 generate_svg.py --prompt "a red circle" [options]

Requires QUIVER_API_KEY or QUIVER_AI_API_KEY environment variable.
"""

import argparse
import json
import os
import sys
import time

import requests


def get_api_key():
    key = os.environ.get("QUIVER_API_KEY") or os.environ.get("QUIVER_AI_API_KEY")
    if not key:
        print(
            "Error: No API key found. Set QUIVER_API_KEY or QUIVER_AI_API_KEY environment variable.",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def main():
    parser = argparse.ArgumentParser(description="Generate SVG from text prompt using Quiver AI")
    parser.add_argument("--prompt", required=True, help="Text description of the SVG to generate")
    parser.add_argument("--output", help="Output file path (default: generated_svg_TIMESTAMP.svg)")
    parser.add_argument("--output-dir", default=".", help="Output directory (default: current directory)")
    parser.add_argument("--instructions", help="Style guidance or additional instructions")
    parser.add_argument("--references", nargs="+", help="Reference image URLs (max 4)")
    parser.add_argument("--n", type=int, default=1, help="Number of SVGs to generate (1-16, default: 1)")
    parser.add_argument("--temperature", type=float, default=1, help="Randomness 0-2 (default: 1)")
    parser.add_argument("--model", default="arrow-preview", help="Model name (default: arrow-preview)")
    parser.add_argument("--timeout", type=int, default=600, help="Request timeout in seconds (default: 600)")
    args = parser.parse_args()

    if args.references and len(args.references) > 4:
        print("Error: Maximum 4 reference images allowed.", file=sys.stderr)
        sys.exit(1)

    if args.n < 1 or args.n > 16:
        print("Error: --n must be between 1 and 16.", file=sys.stderr)
        sys.exit(1)

    if args.temperature < 0 or args.temperature > 2:
        print("Error: --temperature must be between 0 and 2.", file=sys.stderr)
        sys.exit(1)

    api_key = get_api_key()

    # Build request body
    body = {
        "prompt": args.prompt,
        "model": args.model,
        "n": args.n,
        "temperature": args.temperature,
    }

    if args.instructions:
        body["instructions"] = args.instructions

    if args.references:
        body["references"] = [{"url": url} for url in args.references]

    # Make API request
    try:
        response = requests.post(
            "https://api.quiver.ai/v1/svgs/generations",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=args.timeout,
        )
    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed: {e}", file=sys.stderr)
        sys.exit(1)

    if response.status_code != 200:
        print(f"Error: API returned status {response.status_code}", file=sys.stderr)
        try:
            error_data = response.json()
            print(f"Details: {json.dumps(error_data, indent=2)}", file=sys.stderr)
        except Exception:
            print(f"Response: {response.text}", file=sys.stderr)
        sys.exit(1)

    result = response.json()

    # Print usage info to stderr
    if "usage" in result:
        usage = result["usage"]
        print(f"Token usage: {json.dumps(usage)}", file=sys.stderr)

    # Write SVG output(s)
    os.makedirs(args.output_dir, exist_ok=True)
    output_paths = []

    for i, item in enumerate(result.get("data", [])):
        svg_content = item.get("svg", "")

        if args.output and args.n == 1:
            path = os.path.join(args.output_dir, args.output) if not os.path.isabs(args.output) else args.output
        else:
            timestamp = int(time.time())
            suffix = f"_{i + 1}" if args.n > 1 else ""
            filename = args.output if args.output else f"generated_svg_{timestamp}{suffix}.svg"
            if args.n > 1 and args.output:
                base, ext = os.path.splitext(args.output)
                filename = f"{base}_{i + 1}{ext}"
            path = os.path.join(args.output_dir, filename)

        with open(path, "w") as f:
            f.write(svg_content)

        output_paths.append(path)

    # Print output paths to stdout
    for p in output_paths:
        print(p)


if __name__ == "__main__":
    main()
