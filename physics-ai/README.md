# Physics AI Assistant - Agentic System

A fully agentic physics problem-solving system built with LangChain, Chroma DB, and FastAPI.

## 🏗️ Architecture

This system is built as a **true agentic framework** where physics problem-solving is just one capability of the autonomous agent:

### Core Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **LLM** | GPT-4 (OpenAI) | Reasoning and decision making |
| **Agent Framework** | LangChain | Agent orchestration and tool integration |
| **Memory** | Chroma DB | Persistent knowledge and experience storage |
| **Tools** | Custom LangChain Tools | Physics solving, knowledge retrieval, reflection |
| **Reflection** | LangChain prompt chains | Self-evaluation and learning |
| **Orchestration** | FastAPI + Celery | Backend API and task management |

### Agentic Capabilities

The system is **fully agentic** with these autonomous behaviors:

1. **Autonomous Problem Solving** - Uses LangChain agents to solve physics problems
2. **Self-Directed Learning** - Learns from experiences and improves strategies
3. **Exploration** - Explores physics concepts autonomously
4. **Reflection** - Self-evaluates performance and extracts insights
5. **Goal Setting** - Sets and pursues autonomous goals
6. **Memory Management** - Maintains persistent knowledge and experiences

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Redis (for Celery)
- OpenAI API key

### Installation

1. **Clone and install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

3. **Start Redis (for background tasks):**
```bash
redis-server
```

4. **Run the Streamlit app:**
```bash
streamlit run app.py
```

5. **Optional: Start the FastAPI backend:**
```bash
python -m agents.agent_orchestrator
```

## 🧠 How It Works

### Agentic Flow

1. **User Input** → Physics problem text
2. **Agent Decision** → LangChain agent decides how to approach
3. **Tool Execution** → Uses physics tools, knowledge retrieval, reflection
4. **Learning** → Stores experience in Chroma DB memory
5. **Improvement** → Updates strategies based on performance

### Memory System

- **Experiences**: Problem-solving attempts and outcomes
- **Knowledge**: Physics concepts, formulas, examples
- **Strategies**: Solving approaches with success rates
- **Goals**: Autonomous goals and progress tracking

### Autonomous Behaviors

The agent can:
- Solve problems using multiple approaches
- Explore related concepts autonomously
- Learn from failures and successes
- Set and pursue learning goals
- Reflect on its own performance
- Adapt strategies based on experience

## 📁 Project Structure

```
physics-ai/
├── agents/
│   ├── physics_agent.py      # LangChain-based physics agent
│   ├── agent_memory.py       # Chroma DB memory system
│   ├── agent_orchestrator.py # FastAPI + Celery orchestration
│   └── __init__.py
├── core/                     # Physics solving components
├── utils/                    # Data models and utilities
├── config/                   # Configuration
├── app.py                    # Streamlit frontend
└── requirements.txt          # Dependencies
```

## 🔧 Configuration

Key configuration in `config/settings.py`:
- OpenAI API settings
- LLM model selection
- Memory paths
- Agent parameters

## 🎯 Agentic Features

### Autonomous Problem Solving
- Uses LangChain agents with physics tools
- Multiple solving strategies
- Self-verification and reflection

### Persistent Learning
- Chroma DB stores all experiences
- Knowledge graph of physics concepts
- Strategy improvement over time

### Goal-Directed Behavior
- Sets autonomous learning goals
- Tracks progress toward goals
- Adapts behavior based on goals

### Self-Reflection
- Analyzes own performance
- Extracts learning insights
- Updates strategies automatically

## 🔌 API Endpoints

The FastAPI backend provides:

- `POST /solve_problem` - Solve physics problems
- `GET /agent_status` - Get agent status
- `POST /agent_action` - Perform autonomous actions
- `GET /agent_memory` - Access agent memory
- `POST /set_goal` - Set autonomous goals

## 🧪 Testing

Test the agentic capabilities:

```python
from agents.physics_agent import PhysicsAgent

agent = PhysicsAgent()

# Autonomous problem solving
result = agent.solve_problem_autonomously("A pendulum has length 2m. What is its period?")

# Autonomous exploration
exploration = agent.explore_physics_concept("pendulum")

# Learning from experience
learning = agent.learn_from_experience()
```

## 🎨 Frontend

The Streamlit interface provides:
- Problem input and solving
- Real-time agent status
- Autonomous action controls
- Experience and knowledge visualization

## 🔄 Background Tasks

Celery handles:
- Long-running problem solving
- Autonomous exploration
- Learning and reflection tasks
- Memory updates

## 🚀 Deployment

### Local Development
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery worker
celery -A agents.agent_orchestrator worker --loglevel=info

# Terminal 3: FastAPI
python -m agents.agent_orchestrator

# Terminal 4: Streamlit
streamlit run app.py
```

### Production
- Use Redis Cloud for memory
- Deploy FastAPI with uvicorn
- Use Celery with Redis backend
- Configure proper environment variables

## 🤝 Contributing

This is an agentic system - contributions should focus on:
- Improving agent autonomy
- Adding new tools and capabilities
- Enhancing learning mechanisms
- Expanding knowledge representation

## 📄 License

MIT License - see LICENSE file for details.

---

**This is a true agentic system where physics problem-solving is just one capability of an autonomous, learning agent.**
