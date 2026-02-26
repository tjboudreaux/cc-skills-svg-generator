#!/usr/bin/env python3
"""
Convert raster images to SVG using the Quiver AI API.

Usage:
    python3 vectorize_svg.py --image photo.png [options]
    python3 vectorize_svg.py --image https://example.com/photo.png [options]

Requires QUIVER_API_KEY or QUIVER_AI_API_KEY environment variable.
"""

import argparse
import base64
import json
import mimetypes
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


def is_url(path):
    return path.startswith("http://") or path.startswith("https://")


def encode_image(file_path):
    """Read a local image file and return a base64 data URI."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "image/png"

    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{data}"


def main():
    parser = argparse.ArgumentParser(description="Vectorize raster image to SVG using Quiver AI")
    parser.add_argument("--image", required=True, help="Local file path or URL of image to vectorize")
    parser.add_argument("--output", help="Output file path (default: vectorized_TIMESTAMP.svg)")
    parser.add_argument("--output-dir", default=".", help="Output directory (default: current directory)")
    parser.add_argument("--auto-crop", action="store_true", help="Enable automatic cropping")
    parser.add_argument("--target-size", type=int, help="Target size in pixels (128-4096)")
    parser.add_argument("--n", type=int, default=1, help="Number of SVGs to generate (1-16, default: 1)")
    parser.add_argument("--temperature", type=float, default=1, help="Randomness 0-2 (default: 1)")
    parser.add_argument("--model", default="arrow-preview", help="Model name (default: arrow-preview)")
    parser.add_argument("--timeout", type=int, default=600, help="Request timeout in seconds (default: 600)")
    args = parser.parse_args()

    if args.n < 1 or args.n > 16:
        print("Error: --n must be between 1 and 16.", file=sys.stderr)
        sys.exit(1)

    if args.temperature < 0 or args.temperature > 2:
        print("Error: --temperature must be between 0 and 2.", file=sys.stderr)
        sys.exit(1)

    if args.target_size is not None and (args.target_size < 128 or args.target_size > 4096):
        print("Error: --target-size must be between 128 and 4096.", file=sys.stderr)
        sys.exit(1)

    api_key = get_api_key()

    # Build image input
    if is_url(args.image):
        image_input = {"url": args.image}
    else:
        if not os.path.isfile(args.image):
            print(f"Error: File not found: {args.image}", file=sys.stderr)
            sys.exit(1)
        image_input = {"url": encode_image(args.image)}

    # Build request body
    body = {
        "image": image_input,
        "model": args.model,
        "n": args.n,
        "temperature": args.temperature,
    }

    if args.auto_crop:
        body["auto_crop"] = True

    if args.target_size is not None:
        body["target_size"] = args.target_size

    # Make API request
    try:
        response = requests.post(
            "https://api.quiver.ai/v1/svgs/vectorizations",
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
            filename = args.output if args.output else f"vectorized_{timestamp}{suffix}.svg"
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
