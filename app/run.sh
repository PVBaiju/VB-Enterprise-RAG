#!/bin/bash
# Suppress PyTorch/Streamlit compatibility warning
export PYTHONWARNINGS="ignore"
cd "$(dirname "$0")"
python3 -m streamlit run app.py --logger.level=error 2>&1 | grep -v "Examining the path of torch" | grep -v "RuntimeError: no running event loop" | grep -v "RuntimeError: Tried to instantiate class"
