# Makefile — One-command Outback-Safe USB build orchestrator.
#
# Usage:
#   make                    # Full build into build/output/, then copy to USB
#   make all USB=/Volumes/OUTBACK_SAFE
#   make deps               # Just bundle Python deps
#   make copy               # Just copy to USB (assumes prior build)
#   make binaries-win       # Fetch Windows llama-server binary
#   make deps-win           # Bundle Windows Python deps
#   make verify-win         # Verify Windows build
#   make clean              # Remove build/output/

USB          ?= /Volumes/OUTBACK_SAFE
VAULT        ?= "$(HOME)/Survival-Wiki/Outback Safe - Obsidian Vault"
BUILD_OUTPUT ?= build/output

.PHONY: all preprocess emergency index models binaries deps copy clean binaries-win deps-win verify-win

all: preprocess emergency index models binaries deps copy

preprocess:
	python3 build/preprocess.py --source $(VAULT) --output $(BUILD_OUTPUT)/outback-safe/

emergency:
	python3 build/generate_emergency_pages.py --source $(BUILD_OUTPUT)/outback-safe/ --output $(BUILD_OUTPUT)/outback-safe/index.html

index:
	python3 build/build_search_index.py --content $(BUILD_OUTPUT)/outback-safe/ --user-content $(BUILD_OUTPUT)/content/ --chunk-size 500 --chunk-overlap 50 --output $(BUILD_OUTPUT)/search_index.json

models:
	python3 build/download_models.py --output $(BUILD_OUTPUT)/models/

binaries:
	python3 build/fetch_llama_binaries.py --output $(BUILD_OUTPUT)/bin/

deps:
	python3 build/bundle_deps.py --output $(BUILD_OUTPUT)/

copy:
	@echo "📀 Copying to USB..."
	rm -rf $(USB)/outback-safe $(USB)/ai $(USB)/content 2>/dev/null || true
	cp -r $(BUILD_OUTPUT)/outback-safe $(USB)/
	mkdir -p $(USB)/ai/app $(USB)/content
	cp -r $(BUILD_OUTPUT)/models $(USB)/ai/
	cp -r $(BUILD_OUTPUT)/bin $(USB)/ai/
	cp -r $(BUILD_OUTPUT)/deps-arm64 $(USB)/ai/ 2>/dev/null || true
	cp -r $(BUILD_OUTPUT)/deps-x64 $(USB)/ai/ 2>/dev/null || true
	cp -r $(BUILD_OUTPUT)/deps-win64 $(USB)/ai/ 2>/dev/null || true
	cp $(BUILD_OUTPUT)/search_index.json $(USB)/ai/app/
	cp build/build_search_index.py $(USB)/ai/app/
	cp build/*.sh $(USB)/ai/ 2>/dev/null || true
	cp build/*.command $(USB)/ai/ 2>/dev/null || true
	cp -r $(BUILD_OUTPUT)/bin/*.dll $(USB)/ai/bin/ 2>/dev/null || true
	chmod +x $(USB)/ai/bin/llama-server-* 2>/dev/null || true
	xattr -cr $(USB)/ai/ 2>/dev/null || true
	echo "Drop .md files here. Indexed on next launch." > $(USB)/content/README.txt
	@echo "✅ USB build complete: $(USB)"

binaries-win:
	python3 build/fetch_llama_binaries.py --tag b10107 --output $(BUILD_OUTPUT)/bin/ --platform win64

deps-win:
	python3 build/bundle_deps.py --output $(BUILD_OUTPUT)/ --platform win64

verify-win:
	@echo "Verifying Windows build..."
	@test -f $(BUILD_OUTPUT)/bin/llama-server-win64.exe || (echo "❌ Missing exe" && false)
	@test -d $(BUILD_OUTPUT)/deps-win64/flask || (echo "❌ Missing flask dep" && false)
	@test -d $(BUILD_OUTPUT)/deps-win64/numpy || (echo "❌ Missing numpy dep" && false)
	@echo "✅ Windows build verified"

clean:
	rm -rf $(BUILD_OUTPUT)
