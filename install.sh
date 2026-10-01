#!/usr/bin/env bash
# Git Bash/Unix convenience launcher; installation logic lives in install.py.
set -euo pipefail

script_path=${BASH_SOURCE[0]}
script_dir=${script_path%/*}
if [[ "$script_dir" == "$script_path" ]]; then
    script_dir=.
fi
repo_dir=$(cd -- "$script_dir" && pwd -P)

python_command=()
try_python() {
    if command -v "$1" >/dev/null 2>&1 &&
       "$@" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
        python_command=("$@")
        return 0
    fi
    return 1
}
if ! try_python python && ! try_python py -3 && ! try_python python3; then
    printf '%s\n' 'wodtex: Python 3.9+ is required. Install Windows Python (python or py -3) and put it on PATH.' >&2
    exit 1
fi

platform=$("${python_command[@]}" -c 'import os; print(os.name)')
platform_args=()
if [[ "$platform" == nt ]]; then
    # install.py validates both MiKTeX commands before modifying the user tree.
    platform_args=(--miktex)
fi
exec "${python_command[@]}" "$repo_dir/scripts/install.py" "${platform_args[@]}" "$@"
