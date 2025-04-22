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

## Project structure
```
.
├── docker-compose.yaml
├── Makefile
├── pyproject.toml
├── README.md
├── src
│   └── system_assistant
│       ├── application                            # Application layer
│       │   ├── commands                           # Commads (Handled by mediator)
│       │   │   ├── base.py
│       │   │   ├── generate_ai_voice_response.py
│       │   │   ├── __init__.py
│       │   │   └── request_system_help.py
│       │   ├── gateways
│       │   │   ├── chat.py
│       │   │   └── __init__.py
│       │   ├── __init__.py
│       │   ├── mediator.py                        # Mediator (Orchestrates logic)
│       │   ├── queries                            # Queries (Handled by mediator)
│       │   │   ├── base.py
│       │   │   └── __init__.py
│       │   └── services                           # Application services
│       │       ├── ai
│       │       │   ├── base.py
│       │       │   ├── __init__.py
│       │       │   └── prompts.py
│       │       ├── __init__.py
│       │       └── text_to_speech
│       │           ├── base.py
│       │           └── __init__.py
│       ├── core                                   # Core of the project
│       │   ├── config.py
│       │   ├── exceptions.py
│       │   ├── __init__.py
│       │   └── types.py
│       ├── domain                                 # Domain layer
│       │   ├── entities
│       │   │   ├── chat.py
│       │   │   └── __init__.py
│       │   ├── __init__.py
│       │   └── vo.py
│       ├── entry                                  # Main entry points
│       │   ├── cli.py
│       │   └── __init__.py
│       ├── infrastructure                         # Infrastructure layer
│       │   ├── gateways
│       │   │   ├── chat
│       │   │   │   ├── dgraph.py
│       │   │   │   └── __init__.py
│       │   │   └── __init__.py
│       │   ├── __init__.py
│       │   ├── ioc.py                             # DI container
│       │   └── services                           # Infrastructure services
│       │       ├── ai
│       │       │   ├── checkpointer
│       │       │   ├── deepseek.py                # DeepSeek LLM, Agent
│       │       │   ├── gemini.py                  # Gemini LLM, Agent
│       │       │   ├── __init__.py
│       │       │   ├── openai_agent.py
│       │       │   ├── tools                      # Tools used by agents
│       │       │   └── utils.py
│       │       ├── __init__.py
│       │       ├── sound
│       │       │   ├── base.py
│       │       │   ├── __init__.py
│       │       │   └── mpg123.py
│       │       └── text_to_speech
│       │           ├── google.py
│       │           └── __init__.py
│       ├── __init__.py
│       └── py.typed
├── tests                                          # Tests
```

## Configuration
### Environment variables
```
# For text synthezising
GOOGLE_API_KEY=string

# One of this required
DEEPSEEK_API_KEY=string
GEMINI_API_KEY=string
OPENAI_API_KEY=string
```
