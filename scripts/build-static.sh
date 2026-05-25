#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

rm -rf dist
mkdir -p dist/assets/figures

uv run python scripts/preprocess_assets.py

uv run marimo export html mobilanalyse.py \
  --output dist/index.html \
  --no-include-code \
  --force

uv run python scripts/finalize_static_html.py
