#!/bin/bash
cd "$(dirname "$0")"
USB_DIR="$(cd .. && pwd)"

echo "📀 Outback-Safe USB — Starting AI Assistant..."
echo ""

lsof -ti :8765 | xargs kill 2>/dev/null || true
lsof -ti :8766 | xargs kill 2>/dev/null || true
sleep 1

# Find Python: prefer 3.11+, fall back gracefully
PYTHON=""
for py in /opt/homebrew/bin/python3.11 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3 python3.11 python3.12 python3; do
    if command -v "$py" &>/dev/null; then
        ver=$("$py" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        maj=$(echo "$ver" | cut -d. -f1)
        min=$(echo "$ver" | cut -d. -f2)
        if [ "$maj" -ge 3 ] && [ "$min" -ge 10 ]; then
            PYTHON="$py"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ Python 3.10+ not found."
    echo "   Install: brew install python@3.12"
    echo "   Opening survival reference instead..."
    open "$USB_DIR/outback-safe/index.html"
    exit 1
fi

export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
export PYTHONPATH="$USB_DIR/ai/deps-arm64${PYTHONPATH:+:$PYTHONPATH}"

echo "🚀 Starting server (model loads in ~5 seconds)..."
cd "$USB_DIR/ai/app"
exec $PYTHON server.py \
    --usb-dir "$USB_DIR" \
    --llama-bin "$USB_DIR/ai/bin/llama-server-arm64"
