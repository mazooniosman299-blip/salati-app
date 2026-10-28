#!/usr/bin/env bash
set +x
set -euo pipefail
script_directory="$(cd -- "$(dirname -- "$0")" && pwd)"
exec "${SALATI_PYTHON:-python3}" "$script_directory/sign-android.py" "$@"
