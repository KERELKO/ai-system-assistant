# AI System Assistant

An intelligent voice-controlled assistant that helps users interact with their operating system through natural language commands. It can perform file operations, run containers, and assist with various system tasks using voice or text input.

## Features

- **Voice Interaction**: Speak naturally to command your system
- **Text Input**: Type commands when voice isn't convenient
- **System Tools**:
  - File operations (create, delete, modify)
  - Container management (Docker)
  - System information retrieval
  - And more through extensible tools
- **Multiple AI Backends**: Supports DeepSeek, Gemini, and OpenAI
- **Text-to-Speech**: Hear responses from the assistant
- **Context Awareness**: Understands your current working directory

## Installation

| Header 1      | Header 2      | Header 3      |
|---------------|---------------|---------------|
| Row 1 Cell 1  | Row 1 Cell 2  | Row 1 Cell 3  |
| Row 2 Cell 1  | Row 2 Cell 2  | Row 2 Cell 3  |

### Prerequisites

- Python 3.12+
- Docker (for container operations)
- System dependencies:
  - `mpg123` for audio playback (Linux: `sudo apt install mpg123`)

### Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-system-assistant.git
cd ai-system-assistant
```
2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate    # Windows
```
3. Install dependencies:
```bash
pip install -e .
```
### Usage
#### Basic Command
```bash
python3 -m system_assistant.entry.cli --temperature 0 --llm deepseek --chat-id 1 --enable-tools
```
#### Options
| Option | Description | Default |
|--------|-------------|---------- |
|--temperature |	Controls creativity of responses (0.0-2.0) | 1.0 |
|--llm |	AI backend to use (deepseek, gemini, openai) | deepseek |
|--enable-tools	| Allow the AI to use system tools | False |
|--cwd | Current working directory (provides context to the AI)	| Project root |
|--debug | Enable debug mode (disables voice, uses text input) | False |
|--chat-id | Custom chat ID for conversation continuity	Random | UUID |
