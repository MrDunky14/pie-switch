#!/usr/bin/env bash
# ==============================================================================
# pie-Switch Demo Reset Script
# Cleanly restores target_service/app.py to its original buggy state in 2 seconds.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔄 Resetting pie-Switch to baseline demo state..."

# 1. Restore unpatched target_service/app.py from pristine backup
if [ -f "$ROOT_DIR/target_service/app.py.orig" ]; then
    cp "$ROOT_DIR/target_service/app.py.orig" "$ROOT_DIR/target_service/app.py"
    touch "$ROOT_DIR/target_service/app.py"
    echo "  ✔ Restored target_service/app.py to original latent-bug state"
else
    echo "  ⚠️ target_service/app.py.orig not found, keeping existing app.py"
fi

# 2. Reset workspace logs
mkdir -p "$ROOT_DIR/workspace"
> "$ROOT_DIR/workspace/service.log"
echo "  ✔ Cleared ./workspace/service.log"

# 3. Verify workspace repro & patches directories exist
mkdir -p "$ROOT_DIR/workspace/repro"
mkdir -p "$ROOT_DIR/workspace/patches"
echo "  ✔ Verified ./workspace/repro/ and ./workspace/patches/ volumes"

echo "✨ Demo environment reset complete. Ready for 'make chaos' or live demo run."
