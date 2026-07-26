#!/bin/bash
# Reindex the SHTF USB knowledge base
# Run after adding new .md files to content/
cd "$(dirname "$0")"
USB_DIR="$(cd .. && pwd)"

echo "📚 SHTF USB — Reindex Knowledge Base"
echo ""

# Find Python
PYTHON=""
for py in /opt/homebrew/bin/python3.11 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3 python3.12 python3.11 python3; do
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
    echo "❌ Python 3.10+ not found. Install: brew install python@3.12"
    exit 1
fi

echo "Using: $PYTHON"
echo "Content dir: $USB_DIR/content/"
echo "Outback Safe: $USB_DIR/outback-safe/"
echo ""

# Detect arch for deps
ARCH=$(uname -m)
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$USB_DIR/ai/deps-$ARCH:$PYTHONPATH"

# Kill server if running
lsof -ti :8765 | xargs kill 2>/dev/null
lsof -ti :8766 | xargs kill 2>/dev/null
sleep 1

# Rebuild index
echo "🔨 Rebuilding search index..."
cd "$USB_DIR/ai/app"
$PYTHON rag.py \
    --rebuild \
    --content "$USB_DIR/outback-safe/" \
    --user-content "$USB_DIR/content/" \
    --index "$USB_DIR/ai/app/search_index.json"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Reindex complete"
    echo "   Index: ai/app/search_index.json"
    echo ""
    echo "To restart the AI: double-click ai/start.command"
else
    echo ""
    echo "❌ Reindex failed. Check the error above."
    exit 1
fi
