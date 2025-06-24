#!/bin/sh
set -e

echo "➡️  Creating virtual environment at .venv"

uv venv .venv

if [ ! -x ".venv/bin/python" ]; then
  echo "❌ Nem található vagy nem futtatható .venv/bin/python"
  exit 1
fi

echo "✅ Virtuális környezet létrehozva"

echo "➡️  Linkelés /usr/local/bin/python és pip"

ln -sf "$(pwd)/.venv/bin/python" /usr/local/bin/python
ln -sf "$(pwd)/.venv/bin/python" /usr/local/bin/python3
ln -sf "$(pwd)/.venv/bin/pip" /usr/local/bin/pip

echo "✅ Python verzió:"
python --version

