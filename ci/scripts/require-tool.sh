#!/usr/bin/env bash
# Usage: require-tool.sh <command>
# Fails the stage with a clear message when an optional pipeline tool is missing,
# so opt-in stages can never pass without actually running.
set -euo pipefail

tool="${1:?usage: require-tool.sh <command>}"

if ! command -v "$tool" >/dev/null 2>&1; then
    echo "ERROR: '$tool' is not installed on this Jenkins agent." >&2
    echo "Install it or untick the matching build parameter. See docs/security/security-model.md." >&2
    exit 1
fi

echo "Found $tool: $(command -v "$tool")"
"$tool" --version 2>/dev/null | head -n 1 || "$tool" version 2>/dev/null | head -n 1 || true
