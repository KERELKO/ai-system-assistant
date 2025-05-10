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
| Option           | Description                                                                                          | Default      |
| ---------------- | ---------------------------------------------------------------------------------------------------- | ------------ |
| `--llm`          | AI backend to use. Available: `deepseek`, `gemini`                                                   | `deepseek`   |
| `--temperature`  | Controls creativity of responses (range: 0.0–2.0)                                                    | `1.0`        |
| `--enable-tools` | Allow the AI to use system tools                                                                     | `False`      |
| `--cwd`          | Current working directory. Use to provide rich LLM context                                           | Project root |
| `--debug`        | Enable debug mode. In this mode, logging level is set to DEBUG                                       | `False`      |
| `--storage`      | Storage backend to persist chat history. Available: `memory`, `sqlite`, `dgraph`                     | `memory`     |
| `--chat-id`      | Provide custom chat ID. Useful for loading/saving conversation history if persistent storage is used | `None`       |
| `--input`        | Input type. Available: `text`, `voice`. If `voice` is selected, microphone will be used              | `text`       |
| `--output`       | Output type. Available: `text`, `voice`. If `voice` is selected, assistant will speak responses      | `text`       |

### AI Tools
Here is the list of tools that can be used by AI if system tools allowed

#### OS
  - `create_file`
  - `create_folder`
  - `delete_file`
  - `change_permissions`
  - `delete_file`
  - `delete_folder`
  - `is_valid_path`
  - `list_dir`
#### Docker
  - `list_docker_containers`
  - `build_docker_image`
  - `run_docker_container`
  - `run_docker_compose`
  - `stop_docker_container`
  - `stop_docker_compose`
#### Search
  - `brave_search` (`BRAVE_SEARCH_API_KEY` environment variable required)

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
│       │   ├── commands/                          # Commands (Handled by mediator)
│       │   ├── gateways/
│       │   ├── mediator.py                        # Mediator (Orchestrates logic)
│       │   ├── queries/                           # Queries (Handled by mediator)
│       │   └── services                           # Application services
│       │       ├── ai
│       │       └── text_to_speech
│       ├── core                                   # Core of the project
│       │   ├── config.py
│       │   ├── exceptions.py
│       │   └── types.py
│       ├── domain/                                # Domain layer
│       ├── entry/                                 # Main entry points
│       ├── infrastructure                         # Infrastructure layer
│       │   ├── gateways
│       │   │   └── chat
│       │   ├── __init__.py
│       │   ├── ioc.py                             # DI container
│       │   └── services                           # Infrastructure services
│       │       ├── ai
│       │       │   ├── deepseek.py                # DeepSeek LLM, Agent
│       │       │   ├── gemini.py                  # Gemini LLM, Agent
│       │       │   ├── __init__.py
│       │       │   ├── openai_agent.py            # Base OpenAI agent
│       │       │   ├── tools/                     # Tools used by agents
│       │       │   └── utils.py
│       │       ├── __init__.py
│       │       ├── sound/
│       │       └── text_to_speech/
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
