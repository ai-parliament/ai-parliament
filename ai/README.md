# AI Module 🤖

The AI module contains the core multi-agent simulation engine for the AI Parliament system. It implements sophisticated AI agents that simulate political parties, individual politicians, and a supervisor that orchestrates the entire parliamentary process.

## 🏗️ Architecture

The AI module follows a hierarchical multi-agent architecture:

```
Supervisor Agent
├── Party Agent 1
│   ├── Politician Agent 1.1
│   ├── Politician Agent 1.2
│   └── Politician Agent 1.3
├── Party Agent 2
│   ├── Politician Agent 2.1
│   └── Politician Agent 2.2
└── ...
```

## 📁 Structure

```
ai/
├── 📄 pyproject.toml              # Module configuration
├── 📄 requirements.txt            # Dependencies
└── 📁 src/
    ├── 📁 agents/                 # AI agent implementations
    │   ├── base_agent.py          # Abstract base class for all agents
    │   ├── party_agent.py         # Political party agent
    │   ├── politician_agent.py    # Individual politician agent
    │   └── supervisor_agent.py    # Simulation orchestrator
    ├── 📁 database/               # Data storage and retrieval
    │   └── vector_database.py     # Vector database for knowledge storage
    ├── 📁 simulation/             # Simulation logic
    │   ├── parliament_simulation.py # Main simulation controller
    │   └── voting_system.py       # Voting mechanics and tallying
    ├── 📁 utilities/              # Helper functions and utilities
    │   └── prompt_manager.py      # AI prompt management
    └── 📄 prompts.yml             # Prompt templates and configurations
```

## 🤖 Agent Types

### Base Agent (`base_agent.py`)

Abstract base class providing common functionality:
- Environment variable loading
- LLM initialization (OpenAI ChatGPT)
- Memory management
- Prompt management integration

**Key Features:**
- Automatic `.env` file loading
- Configurable model selection
- Built-in conversation memory
- Error handling and logging

### Supervisor Agent (`supervisor_agent.py`)

Orchestrates the entire parliamentary simulation:
- Manages simulation phases
- Coordinates between parties
- Tracks overall progress
- Generates final summaries

**Responsibilities:**
- Initialize all party and politician agents
- Manage intra-party deliberations
- Facilitate inter-party debates
- Conduct final voting
- Compile comprehensive results

### Party Agent (`party_agent.py`)

Represents a political party:
- Manages internal party discussions
- Coordinates politician agents
- Forms party positions
- Negotiates with other parties

**Capabilities:**
- Internal deliberation management
- Consensus building
- Position articulation
- Inter-party negotiation

### Politician Agent (`politician_agent.py`)

Represents individual politicians:
- Unique personality and viewpoints
- Personal voting decisions
- Participation in discussions
- Individual argumentation

**Characteristics:**
- Personalized prompts based on role
- Individual decision-making
- Argument generation
- Vote casting

## 🗄️ Database Integration

### Vector Database (`vector_database.py`)

Handles knowledge storage and retrieval:
- FAISS-based vector storage
- Semantic search capabilities
- Knowledge base management
- Context retrieval for agents

**Features:**
- Efficient similarity search
- Scalable storage
- Real-time updates
- Context-aware retrieval

## 🎯 Simulation Components

### Parliament Simulation (`parliament_simulation.py`)

Main simulation controller:
- Phase management
- Agent coordination
- State tracking
- Result compilation

**Simulation Phases:**
1. **Initialization**: Set up agents and context
2. **Intra-Party Deliberation**: Internal party discussions
3. **Inter-Party Debate**: Cross-party negotiations
4. **Voting**: Individual vote collection
5. **Results**: Summary generation

### Voting System (`voting_system.py`)

Handles the democratic voting process:
- Vote collection
- Tally calculation
- Result determination
- Statistical analysis

**Voting Features:**
- Individual vote tracking
- Party-wise analysis
- Majority determination
- Detailed breakdowns

## 🛠️ Utilities

### Prompt Manager (`prompt_manager.py`)

Manages AI prompts and templates:
- YAML-based prompt storage
- Dynamic prompt generation
- Context injection
- Template management

**Prompt Types:**
- Agent initialization prompts
- Discussion facilitation prompts
- Voting instruction prompts
- Summary generation prompts

## 📋 Dependencies

Key dependencies include:
- **LangChain**: Agent framework and LLM integration
- **LangGraph**: Multi-agent orchestration
- **OpenAI**: Language model API
- **FAISS**: Vector database
- **PyYAML**: Configuration management
- **python-dotenv**: Environment variable management

## 🚀 Usage

### Standalone Usage

```python
from src.simulation.parliament_simulation import ParliamentSimulation

# Initialize simulation
simulation = ParliamentSimulation()

# Configure parties and politicians
parties = [
    {
        "name": "Progressive Party",
        "politicians": [
            {"name": "Alice Johnson", "role": "Leader"},
            {"name": "Bob Smith", "role": "Member"}
        ]
    }
]

# Run simulation
results = simulation.run_simulation(
    topic="Climate Change Legislation",
    parties=parties
)
```

### Integration with Backend

The AI module is designed to be used through the backend API:

```python
from src.api.ai_service import AIService

ai_service = AIService()
results = ai_service.run_full_simulation(simulation_data)
```

## ⚙️ Configuration

### Environment Variables

Required environment variables:
```env
OPENAI_API_KEY=your_openai_api_key
GPT_MODEL_NAME=gpt-4o-mini
LANGSMITH_API_KEY=your_langsmith_key  # Optional
```

### Prompt Configuration

Prompts are configured in `prompts.yml`:
```yaml
agents:
  supervisor:
    system_prompt: "You are a parliamentary supervisor..."
  party:
    system_prompt: "You represent a political party..."
  politician:
    system_prompt: "You are a politician with specific views..."
```

## 🧪 Testing

Run AI module tests:
```bash
cd ai
python -m pytest tests/
```

Test individual components:
```bash
# Test agents
python -m pytest tests/test_agents.py

# Test simulation
python -m pytest tests/test_simulation.py

# Test database
python -m pytest tests/test_database.py
```

## 🔧 Development

### Adding New Agents

1. Inherit from `BaseAgent`
2. Implement required abstract methods
3. Add agent-specific functionality
4. Update prompt templates
5. Register with supervisor

### Extending Simulation

1. Modify `parliament_simulation.py`
2. Add new phases or steps
3. Update agent interactions
4. Test thoroughly

### Custom Prompts

1. Edit `prompts.yml`
2. Add new prompt templates
3. Update `prompt_manager.py` if needed
4. Test with different scenarios

## 🐛 Troubleshooting

### Common Issues

1. **Agent Initialization Failures**
   - Check environment variables
   - Verify OpenAI API key
   - Ensure model availability

2. **Memory Issues**
   - Monitor conversation length
   - Implement memory pruning
   - Use streaming for long conversations

3. **Prompt Issues**
   - Validate YAML syntax
   - Check prompt templates
   - Test with simple scenarios

### Performance Optimization

- Use appropriate model sizes
- Implement caching where possible
- Optimize prompt lengths
- Monitor API usage and costs

## 📚 Further Reading

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Multi-Agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system)