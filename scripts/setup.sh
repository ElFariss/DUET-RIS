#!/usr/bin/env bash
set -euo pipefail
# Install uv separately or provide UV=/path/to/uv. No system Python changes.
uvbin="${UV:-uv}"
"$uvbin" venv --python 3.12 .venv
"$uvbin" pip install --python .venv/bin/python -r requirements-lock.txt --torch-backend=cu128
"$uvbin" pip install --python .venv/bin/python -e .
.venv/bin/python -m unittest discover -s tests -v
