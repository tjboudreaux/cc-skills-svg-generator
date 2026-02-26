"""MCP server exposing SVG generation and vectorization tools via the Quiver AI API."""

import base64
import json
import mimetypes
import os
import time

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "svg-generator",
    instructions="Generate SVG images from text prompts or vectorize raster images using the Quiver AI API",
)


def _get_api_key() -> str:
    key = os.environ.get("QUIVER_API_KEY") or os.environ.get("QUIVER_AI_API_KEY")
    if not key:
        raise ValueError(
            "No API key found. Set QUIVER_API_KEY or QUIVER_AI_API_KEY environment variable."
        )
    return key


@mcp.tool()
def generate_svg(
    prompt: str,
    output: str | None = None,
    output_dir: str = ".",
    instructions: str | None = None,
    references: list[str] | None = None,
    n: int = 1,
    temperature: float = 1.0,
    model: str = "arrow-preview",
    timeout: int = 600,
) -> str:
    """Generate SVG images from a text description using the Quiver AI API.

    Args:
        prompt: Text description of the SVG to generate
        output: Output filename (default: generated_svg_TIMESTAMP.svg)
        output_dir: Output directory (default: current directory)
        instructions: Style guidance or additional instructions
        references: Reference image URLs (max 4)
        n: Number of SVGs to generate (1-16, default: 1)
        temperature: Randomness 0-2 (default: 1.0)
        model: Model name (default: arrow-preview)
        timeout: Request timeout in seconds (default: 600)
    """
    api_key = _get_api_key()

    if references and len(references) > 4:
        return "Error: Maximum 4 reference images allowed."
    if n < 1 or n > 16:
        return "Error: n must be between 1 and 16."
    if temperature < 0 or temperature > 2:
        return "Error: temperature must be between 0 and 2."

    body: dict = {
        "prompt": prompt,
        "model": model,
        "n": n,
        "temperature": temperature,
    }
    if instructions:
        body["instructions"] = instructions
    if references:
        body["references"] = [{"url": url} for url in references]

    try:
        response = requests.post(
            "https://api.quiver.ai/v1/svgs/generations",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=timeout,
        )
    except requests.exceptions.RequestException as e:
        return f"Error: Request failed: {e}"

    if response.status_code != 200:
        try:
            error_data = response.json()
            return (
                f"Error: API returned status {response.status_code}\n"
                f"Details: {json.dumps(error_data, indent=2)}"
            )
        except Exception:
            return (
                f"Error: API returned status {response.status_code}\n"
                f"Response: {response.text}"
            )

    result = response.json()
    data = result.get("data", [])

    # Write SVGs to disk
    os.makedirs(output_dir, exist_ok=True)
    paths: list[str] = []
    for i, item in enumerate(data):
        svg_content = item.get("svg", "")
        if output and n == 1:
            path = (
                os.path.join(output_dir, output)
                if not os.path.isabs(output)
                else output
            )
        else:
            timestamp = int(time.time())
            suffix = f"_{i + 1}" if n > 1 else ""
            filename = output or f"generated_svg_{timestamp}{suffix}.svg"
            if n > 1 and output:
                base, ext = os.path.splitext(output)
                filename = f"{base}_{i + 1}{ext}"
            path = os.path.join(output_dir, filename)
        with open(path, "w") as f:
            f.write(svg_content)
        paths.append(path)

    # Build response
    parts: list[str] = []
    if "usage" in result:
        parts.append(f"Token usage: {json.dumps(result['usage'])}")
    parts.append(f"Generated {len(paths)} SVG(s):")
    for p in paths:
        parts.append(f"  {p}")
    if len(data) == 1:
        svg = data[0].get("svg", "")
        if len(svg) < 50000:
            parts.append(f"\nSVG content:\n{svg}")
    return "\n".join(parts)


@mcp.tool()
def vectorize_svg(
    image: str,
    output: str | None = None,
    output_dir: str = ".",
    auto_crop: bool = False,
    target_size: int | None = None,
    n: int = 1,
    temperature: float = 1.0,
    model: str = "arrow-preview",
    timeout: int = 600,
) -> str:
    """Convert a raster image (PNG, JPG, WebP) to SVG vector format using the Quiver AI API.

    Args:
        image: Local file path or URL of the image to vectorize
        output: Output filename (default: vectorized_TIMESTAMP.svg)
        output_dir: Output directory (default: current directory)
        auto_crop: Enable automatic cropping
        target_size: Target size in pixels (128-4096)
        n: Number of SVGs to generate (1-16, default: 1)
        temperature: Randomness 0-2 (default: 1.0)
        model: Model name (default: arrow-preview)
        timeout: Request timeout in seconds (default: 600)
    """
    api_key = _get_api_key()

    if n < 1 or n > 16:
        return "Error: n must be between 1 and 16."
    if temperature < 0 or temperature > 2:
        return "Error: temperature must be between 0 and 2."
    if target_size is not None and (target_size < 128 or target_size > 4096):
        return "Error: target_size must be between 128 and 4096."

    # Build image input
    if image.startswith("http://") or image.startswith("https://"):
        image_input: dict = {"url": image}
    else:
        if not os.path.isfile(image):
            return f"Error: File not found: {image}"
        mime_type, _ = mimetypes.guess_type(image)
        if not mime_type:
            mime_type = "image/png"
        with open(image, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        image_input = {"url": f"data:{mime_type};base64,{encoded}"}

    body: dict = {
        "image": image_input,
        "model": model,
        "n": n,
        "temperature": temperature,
    }
    if auto_crop:
        body["auto_crop"] = True
    if target_size is not None:
        body["target_size"] = target_size

    try:
        response = requests.post(
            "https://api.quiver.ai/v1/svgs/vectorizations",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=timeout,
        )
    except requests.exceptions.RequestException as e:
        return f"Error: Request failed: {e}"

    if response.status_code != 200:
        try:
            error_data = response.json()
            return (
                f"Error: API returned status {response.status_code}\n"
                f"Details: {json.dumps(error_data, indent=2)}"
            )
        except Exception:
            return (
                f"Error: API returned status {response.status_code}\n"
                f"Response: {response.text}"
            )

    result = response.json()
    data = result.get("data", [])

    # Write SVGs to disk
    os.makedirs(output_dir, exist_ok=True)
    paths: list[str] = []
    for i, item in enumerate(data):
        svg_content = item.get("svg", "")
        if output and n == 1:
            path = (
                os.path.join(output_dir, output)
                if not os.path.isabs(output)
                else output
            )
        else:
            timestamp = int(time.time())
            suffix = f"_{i + 1}" if n > 1 else ""
            filename = output or f"vectorized_{timestamp}{suffix}.svg"
            if n > 1 and output:
                base, ext = os.path.splitext(output)
                filename = f"{base}_{i + 1}{ext}"
            path = os.path.join(output_dir, filename)
        with open(path, "w") as f:
            f.write(svg_content)
        paths.append(path)

    # Build response
    parts: list[str] = []
    if "usage" in result:
        parts.append(f"Token usage: {json.dumps(result['usage'])}")
    parts.append(f"Vectorized {len(paths)} SVG(s):")
    for p in paths:
        parts.append(f"  {p}")
    if len(data) == 1:
        svg = data[0].get("svg", "")
        if len(svg) < 50000:
            parts.append(f"\nSVG content:\n{svg}")
    return "\n".join(parts)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
