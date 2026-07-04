#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  /usr/bin/python3 -m venv .venv
fi

source .venv/bin/activate
export PIP_DEFAULT_TIMEOUT=1000

python -m pip install --upgrade pip wheel
pip install "setuptools==59.5.0"

echo "[1/5] Installing PyTorch..."
pip install torch torchvision

echo "[2/5] Installing core scientific stack..."
pip install numpy scipy matplotlib trimesh pyrender smplx

echo "[3/5] Installing project requirements..."
pip install -r requirements.txt

echo "[4/5] Installing optional visualization tools..."
pip install open3d || echo "Warning: open3d install failed; 3D GUI features may be unavailable."

echo "[5/5] Installing EasyMocap package..."
pip install -e .

echo
echo "Environment setup complete."
echo "Activate with: source $ROOT/.venv/bin/activate"
python - <<'PY'
import torch
import cv2
import easymocap
print("torch:", torch.__version__)
print("opencv:", cv2.__version__)
print("easymocap:", easymocap.__file__)
PY
