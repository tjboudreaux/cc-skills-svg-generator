# SVG Generator

Generate SVGs from text prompts or convert raster images to SVG using the [Quiver AI](https://quiver.ai) API.

Works as a **cross-platform AI agent skill** (Claude Code, Codex CLI, Gemini CLI, Cursor, Windsurf) and as an **MCP server** (Claude Code, Codex, Cursor, Cline, Roo Code, Claude Desktop).

## Prerequisites

Get an API key from [Quiver AI](https://quiver.ai) and set it as an environment variable:

```bash
export QUIVER_API_KEY="your-api-key-here"
```

## Installation

### Claude Code (Plugin)

```bash
claude plugin add /path/to/cc-skills-svg-generator
```

This installs both the skill (prompt-driven usage) and the MCP server (tool-based usage).

### Claude Code (MCP Server only)

```bash
claude mcp add svg-generator -- uvx svg-generator-mcp
```

### Claude Code (Skill only)

Copy or symlink the `svg-generator/` directory into your skills folder:

```bash
# User-level (all projects)
cp -r svg-generator ~/.claude/skills/svg-generator

# Project-level (this project only)
mkdir -p .claude/skills
cp -r svg-generator .claude/skills/svg-generator
```

### OpenAI Codex CLI

**As a skill:**

```bash
mkdir -p .agents/skills
cp -r svg-generator .agents/skills/svg-generator
```

**As an MCP server** — add to `~/.codex/config.toml`:

```toml
[mcp_servers.svg-generator]
command = "uvx"
args = ["svg-generator-mcp"]
enabled = true
```

### Cursor

Add to `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "svg-generator": {
      "command": "uvx",
      "args": ["svg-generator-mcp"],
      "env": {
        "QUIVER_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Cline / Roo Code

Add via the MCP settings panel, or add to the MCP config file:

```json
{
  "mcpServers": {
    "svg-generator": {
      "command": "uvx",
      "args": ["svg-generator-mcp"],
      "env": {
        "QUIVER_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "svg-generator": {
      "command": "uvx",
      "args": ["svg-generator-mcp"],
      "env": {
        "QUIVER_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Install from PyPI

```bash
pip install svg-generator-mcp
```

Or run directly with `uvx`:

```bash
uvx svg-generator-mcp
```

## MCP Server Tools

The MCP server exposes two tools:

### `generate_svg`

Generate SVGs from text descriptions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Text description of the SVG |
| `output` | string | No | Output filename |
| `output_dir` | string | No | Output directory (default: `.`) |
| `instructions` | string | No | Style guidance |
| `references` | string[] | No | Reference image URLs (max 4) |
| `n` | int | No | Number of SVGs, 1-16 (default: 1) |
| `temperature` | float | No | Randomness 0-2 (default: 1) |
| `model` | string | No | Model name (default: `arrow-preview`) |
| `timeout` | int | No | Request timeout in seconds (default: 600) |

### `vectorize_svg`

Convert raster images (PNG, JPG, WebP) to SVG.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `image` | string | Yes | Local file path or URL |
| `output` | string | No | Output filename |
| `output_dir` | string | No | Output directory (default: `.`) |
| `auto_crop` | bool | No | Enable automatic cropping |
| `target_size` | int | No | Target size in pixels (128-4096) |
| `n` | int | No | Number of SVGs, 1-16 (default: 1) |
| `temperature` | float | No | Randomness 0-2 (default: 1) |
| `model` | string | No | Model name (default: `arrow-preview`) |
| `timeout` | int | No | Request timeout in seconds (default: 600) |

## CLI Scripts

The skill also includes standalone CLI scripts:

```bash
# Text-to-SVG
python3 svg-generator/scripts/generate_svg.py \
  --prompt "a minimalist mountain logo" \
  --output mountain.svg

# Image-to-SVG
python3 svg-generator/scripts/vectorize_svg.py \
  --image photo.png \
  --output vectorized.svg
```

See `svg-generator/SKILL.md` for full CLI documentation.

## Project Structure

```
.
├── .claude-plugin/
│   └── plugin.json           # Claude Code plugin manifest
├── .mcp.json                 # Project-level MCP config
├── svg-generator/
│   ├── SKILL.md              # Cross-platform agent skill
│   ├── references/
│   │   └── api_reference.md
│   └── scripts/
│       ├── generate_svg.py
│       └── vectorize_svg.py
├── src/
│   └── svg_generator_mcp/
│       ├── __init__.py
│       └── server.py         # MCP server implementation
├── pyproject.toml            # Python package config
└── svg-generator.skill       # Packaged skill (zip)
```

## How It Works

| Layer | What | Reaches |
|-------|------|---------|
| **Skill** (`SKILL.md`) | Instructions + CLI scripts the AI follows | Claude Code, Codex CLI, Gemini CLI, Cursor, Windsurf, GitHub Copilot |
| **MCP Server** | Structured tool API over Model Context Protocol | Claude Code, Claude Desktop, Codex CLI, Cursor, Cline, Roo Code |
| **Plugin** (`.claude-plugin/`) | Bundles skill + MCP server config | Claude Code |

## License

MIT
