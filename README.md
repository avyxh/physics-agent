# Agentic Physics System

A modern, fully agentic system for physics problem solving, built with LangChain, ChromaDB, FastAPI, and Celery.

## Architecture

| Component      | Technology         | Purpose                                 |
|---------------|--------------------|-----------------------------------------|
| LLM           | GPT-4 (OpenAI)     | Reasoning, tool selection, reflection   |
| Agent Framework| LangChain         | Agent orchestration, tool use           |
| Memory        | ChromaDB           | Persistent, semantic memory             |
| Tools         | LangChain Tools    | Physics solver, knowledge, reflection   |
| Reflection    | LLM prompt chain   | Self-evaluation, learning               |
| Orchestration | FastAPI + Celery   | Backend, async task management          |

## Features
- Autonomous problem solving
- Modular tool use (LLM-driven)
- Persistent, semantic memory
- Reflection and learning
- API orchestration and async tasks

## Quick Start

### Prerequisites
- Python 3.8+
- Redis (for Celery)
- OpenAI API key

### Installation
```bash
pip install -r requirements.txt
```

### Environment
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Run the System

1. **Start Redis**
```bash
redis-server
```

2. **Start Celery Worker**
```bash
celery -A agents.agentic_orchestrator worker --loglevel=info
```

3. **Start FastAPI Backend**
```bash
uvicorn agents.agentic_orchestrator:app --reload
```

4. **(Optional) Run Streamlit Frontend**
```bash
streamlit run app.py
```

## Usage

- POST `/solve_problem` with `{ "problem_text": "A ball falls from 10m. What is its final velocity?" }`
- GET `/task_status/{task_id}` to check result
- GET `/health` for health check

## Extending
- Add new tools in `agents/agentic_tools.py`
- Add new memory types in `agents/agentic_memory.py`
- Add new agent behaviors in `agents/agentic_agent.py`

## License
MIT 