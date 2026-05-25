#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

rm -rf dist
mkdir -p dist/data

cp data/mobil.parquet dist/data/mobil.parquet

uv run marimo export html-wasm mobilanalyse.py \
  --output dist \
  --mode run \
  --no-show-code \
  --force
