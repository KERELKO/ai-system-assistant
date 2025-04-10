.PHONY: run
run:
	uv run src/voice_assistant/main.py

.PHONY: clean
clean:
    find src -type d -name "__pycache__" -exec rm -rf
