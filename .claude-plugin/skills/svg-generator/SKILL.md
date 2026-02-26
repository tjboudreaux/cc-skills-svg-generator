---
name: svg-generator
description: >-
  Generate SVG images using the Quiver AI API. Use when the user needs to create
  SVGs from text descriptions (logos, icons, illustrations, calligraphy, diagrams)
  or convert raster images (PNG, JPG, WebP) to SVG vector format. Triggers include
  "generate an SVG", "create a vector image", "make an SVG logo", "convert to SVG",
  "vectorize this image", or any AI-powered SVG creation task.
---

# SVG Generator

Generate SVGs from text prompts or convert raster images to SVG using the Quiver AI API.

## Prerequisites

Set your API key as an environment variable:

```bash
export QUIVER_API_KEY="your-api-key-here"
```

(Also accepts `QUIVER_AI_API_KEY` as a fallback.)

## Workflow Decision Tree

1. **Does the user want to create an SVG from a text description?** → Use Text-to-SVG Generation
2. **Does the user want to convert an existing image to SVG?** → Use Image-to-SVG Vectorization

---

## Text-to-SVG Generation

Generate SVGs from natural language descriptions — logos, icons, illustrations, calligraphy, diagrams, and more.

**Script:** `scripts/generate_svg.py`

### Basic Usage

```bash
python3 scripts/generate_svg.py --prompt "a minimalist mountain logo in blue"
```

### With Style Instructions

```bash
python3 scripts/generate_svg.py \
  --prompt "a coffee cup icon" \
  --instructions "flat design, single color, no gradients" \
  --output coffee_icon.svg
```

### Multiple Variations

```bash
python3 scripts/generate_svg.py \
  --prompt "abstract geometric pattern" \
  --n 4 \
  --temperature 1.5 \
  --output-dir ./variations
```

### With Reference Images

```bash
python3 scripts/generate_svg.py \
  --prompt "a logo similar to this style" \
  --references https://example.com/style-ref.png
```

### All Options

| Flag | Required | Description |
|------|----------|-------------|
| `--prompt` | Yes | Text description of the SVG |
| `--output` | No | Output filename (default: `generated_svg_TIMESTAMP.svg`) |
| `--output-dir` | No | Output directory (default: `.`) |
| `--instructions` | No | Style guidance |
| `--references` | No | Reference image URLs (max 4) |
| `--n` | No | Number of SVGs (1-16, default: 1) |
| `--temperature` | No | Randomness 0-2 (default: 1) |
| `--model` | No | Model name (default: `arrow-preview`) |
| `--timeout` | No | Request timeout in seconds (default: 600) |

---

## Image-to-SVG Vectorization

Convert raster images (PNG, JPG, WebP) to clean SVG vector format. Accepts local files or URLs.

**Script:** `scripts/vectorize_svg.py`

### From a Local File

```bash
python3 scripts/vectorize_svg.py --image logo.png --output logo.svg
```

### From a URL

```bash
python3 scripts/vectorize_svg.py --image https://example.com/photo.jpg --output vectorized.svg
```

### With Auto-Crop and Target Size

```bash
python3 scripts/vectorize_svg.py \
  --image icon.png \
  --auto-crop \
  --target-size 512 \
  --output clean_icon.svg
```

### All Options

| Flag | Required | Description |
|------|----------|-------------|
| `--image` | Yes | Local file path or URL |
| `--output` | No | Output filename (default: `vectorized_TIMESTAMP.svg`) |
| `--output-dir` | No | Output directory (default: `.`) |
| `--auto-crop` | No | Enable automatic cropping (flag) |
| `--target-size` | No | Target size in pixels (128-4096) |
| `--n` | No | Number of SVGs (1-16, default: 1) |
| `--temperature` | No | Randomness 0-2 (default: 1) |
| `--model` | No | Model name (default: `arrow-preview`) |
| `--timeout` | No | Request timeout in seconds (default: 600) |

---

## Output Handling

- **stdout**: Output file path(s), one per line — use this to locate generated files
- **stderr**: Token usage statistics and any error messages
- When `--n > 1`, files are suffixed with `_1`, `_2`, etc.

## Resources

- Full API parameter documentation: [references/api_reference.md](references/api_reference.md)
