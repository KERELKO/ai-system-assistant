.PHONY: run
run:
	python3 -m system_assistant.entry.cli --temperature 0 --llm deepseek --chat-id 1 --enable-tools
