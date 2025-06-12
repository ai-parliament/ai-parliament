# AI Parliament 🏛️

AI Parliament is an advanced simulation of a parliamentary system where AI agents representing political parties and politicians collaborate, debate, and decide on legislative proposals. The system uses LangGraph, LangChain, and OpenAI to create realistic political deliberations and voting processes.

## 🚀 Features

- **Multi-Agent Parliamentary Simulation**: Realistic simulation of political parties and individual politicians
- **Interactive Web Interface**: User-friendly Streamlit frontend for configuring and running simulations
- **Real-time Deliberations**: Watch as parties debate internally and negotiate with each other
- **Configurable Scenarios**: Create custom political parties, politicians, and legislative topics
- **Comprehensive Voting System**: Full parliamentary voting process with detailed results
- **Docker-Ready**: One-command deployment with Docker Compose
- **Environment Variable Support**: Secure configuration management

## Problem Description

The modern political landscape is characterized by high complexity, competing interests, and a lack of transparent mechanisms that allow citizens and analysts to simulate the legislative process.

Moreover, the legislative process in parliamentary democracies relies on negotiations and decisions made both at the level of political parties and individual MPs, making it difficult to predict voting outcomes.

There is a lack of tools that:

- Simulate political decision-making processes in a way that is understandable to the average citizen.
- Allow users to experiment with political scenarios (e.g., "Would law X pass if politicians Y voted?").
- Use artificial intelligence to simulate the behavior of political agents (parties, politicians).
- Combine data from open knowledge sources (e.g., Wikipedia) and analyze them in the context of legislation.

## Solution Description

We propose building a parliamentary voting simulator based on a multi-agent system built using LangGraph, reflecting democratic processes in an interactive and realistic way.

### Key Components of the Solution

1. User
    Asks a question such as: “Would a law about X pass in the parliament?”
    Selects 4 parties and 3 politicians for each from a list.

2. Supervisor Agent

    Manages the coordination of the system and information flow.
    Knows the (simulated) outcome but does not reveal it—its role is to oversee the decision-making process.

3. Research Agent

    Automatically searches for data from Wikipedia about parties and politicians.
    Stores the data in a vector database and graph database (e.g., Neo4j).
    Includes a component for transforming data into system prompt format.

4. Agent Loader

    Loads biographical and political context data for each politician.
    Creates unique system prompts (e.g., ideology, past votes, public statements).

5. Intra-Party Deliberation (Parallel)

    Each of the 4 parties holds an internal debate (asynchronously).
    Politicians exchange arguments, negotiate, and form the party’s position.
    The system allows loops to reach consensus (or note its absence).

6. Inter-Party Debate

    Political parties present their positions.
    They may attempt to persuade other parties to change their stance.
    Simulates negotiations between political groups.

7. Voting and Decision

    Finally, the system collects votes and determines whether the bill passes or fails.
    The result is transparent and includes justification.

### Technologies Used

- **LangGraph** – builds the agent and process flow graph
- **LangChain Agents & Tools** – knowledge retrieval, multi-agent system
- **Wikipedia API / RAG** – pulls data from external sources
- **Vector Databases** – e.g., FAISS
- **LangSmith** – agent tracking, versioning, and monitoring
- **Streamlit** – user interface
- **Docker** – one-command deployment

### Goal

To create a democratic, transparent, and interactive model simulating parliamentary voting, which can serve as:

- An educational tool
- A prototype for modern civic engagement systems
- An inspiration for applying GenAI to model socio-political processes

## 📁 Project Structure

```
ai-parliament/
├── 📁 ai/                                  # AI agents and simulation logic
│   ├── 📄 pyproject.toml                  # AI module configuration
│   ├── 📄 requirements.txt                # AI dependencies
│   └── 📁 src/
│       ├── 📁 agents/                     # AI agent implementations
│       │   ├── base_agent.py              # Base class for all agents
│       │   ├── party_agent.py             # Political party agent
│       │   ├── politician_agent.py        # Individual politician agent
│       │   └── supervisor_agent.py        # Simulation supervisor
│       ├── 📁 database/                   # Database integrations
│       │   └── vector_database.py         # Vector database for knowledge storage
│       ├── 📁 simulation/                 # Simulation orchestration
│       │   ├── parliament_simulation.py   # Main simulation controller
│       │   └── voting_system.py          # Voting logic and tallying
│       ├── 📁 utilities/                  # Utility functions
│       │   └── prompt_manager.py          # Manages AI prompts
│       └── 📄 prompts.yml                 # AI prompt templates
├── 📁 backend/                            # FastAPI backend service
│   ├── 📄 Dockerfile                      # Backend container configuration
│   ├── 📄 pyproject.toml                  # Backend module configuration
│   ├── 📄 requirements.txt                # Backend dependencies
│   ├── 📄 run_simulation.py               # Standalone simulation runner
│   └── 📁 src/
│       ├── 📄 main.py                     # FastAPI application entry point
│       └── 📁 api/
│           ├── ai_service.py              # AI service integration
│           └── routes.py                  # API endpoints and routing
├── 📁 frontend/                           # Streamlit web interface
│   ├── 📄 Dockerfile                      # Frontend container configuration
│   ├── 📄 pyproject.toml                  # Frontend module configuration
│   ├── 📄 requirements.txt                # Frontend dependencies
│   ├── 📁 config/                         # Configuration files
│   │   ├── app_config.yml                 # Application settings
│   │   ├── default_parties.yml            # Default political parties
│   │   └── texts.yml                      # UI text and labels
│   └── 📁 src/
│       ├── 📄 app.py                      # Main Streamlit application
│       └── 📄 config_manager.py           # Configuration management
├── 📄 docker-compose.yml                  # Multi-container orchestration
├── 📄 .env                                # Environment variables
├── 📄 .gitignore                          # Git ignore rules
└── 📄 README.md                           # Project documentation
```

## 🛠️ Prerequisites

- **Docker & Docker Compose** (recommended for easy setup)
- **Python 3.11+** (for local development)
- **OpenAI API Key** (required for AI agents)
- **LangSmith API Key** (optional, for monitoring)

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
GPT_MODEL_NAME=gpt-4o-mini

# Optional (for LangSmith monitoring)
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=your_project_name
LANGSMITH_TRACING=true
```

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-parliament
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the application:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - 🌐 **Frontend**: http://localhost:8501
   - 🔧 **Backend API**: http://localhost:8000/api
   - 📊 **API Health Check**: http://localhost:8000/api/health

5. **Stop the application:**
   ```bash
   docker-compose down
   ```

### Local Development Setup

#### Backend Development

```bash
cd backend
pip install -r requirements.txt
python -m src.main
```

#### Frontend Development

```bash
cd frontend
pip install -r requirements.txt
streamlit run src/app.py
```

#### AI Module Development

```bash
cd ai
pip install -r requirements.txt
# Run standalone simulation
cd ../backend
python run_simulation.py
```

## 🎯 How to Use

1. **Configure Parliament**: Set up political parties and politicians in the sidebar
2. **Set Topic**: Enter a legislative topic for debate
3. **Run Simulation**: Watch as parties deliberate internally and debate with each other
4. **View Results**: See the final vote tally and detailed discussion summaries

## 🏗️ Architecture

The system follows a microservices architecture:

- **Frontend (Streamlit)**: User interface and configuration
- **Backend (FastAPI)**: API layer and orchestration
- **AI Module**: Multi-agent simulation engine
- **Docker Compose**: Container orchestration

## 🤖 AI Agents

- **Supervisor Agent**: Orchestrates the entire simulation
- **Party Agent**: Represents political parties and manages internal discussions
- **Politician Agent**: Individual politicians with unique personalities and viewpoints

## 📊 Simulation Process

1. **Initialization**: Create parties and politicians based on user configuration
2. **Legislation Generation**: AI generates detailed legislation from user topic
3. **Intra-Party Deliberation**: Parties discuss internally to form positions
4. **Inter-Party Debate**: Parties negotiate and try to influence each other
5. **Final Voting**: Each politician casts their vote
6. **Results**: Comprehensive summary of the entire process

## 🔧 Configuration

The system supports extensive configuration through YAML files:

- **`frontend/config/app_config.yml`**: Application settings and UI configuration
- **`frontend/config/default_parties.yml`**: Pre-configured political parties
- **`frontend/config/texts.yml`**: UI text and internationalization
- **`ai/src/prompts.yml`**: AI agent prompts and templates

## 🐳 Docker Configuration

The project includes optimized Docker configurations:

- **Multi-stage builds** for smaller image sizes
- **Environment variable support** for secure configuration
- **Health checks** for container monitoring
- **Network isolation** between services

## 🧪 Testing

Run tests for individual modules:

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
python -m pytest

# AI module tests
cd ai
python -m pytest
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Environment Variables Not Loading**
   - Ensure `.env` file is in the project root
   - Check that all required variables are set
   - Restart Docker containers after changes

2. **API Connection Issues**
   - Verify backend is running on port 8000
   - Check Docker network configuration
   - Ensure firewall allows local connections

3. **OpenAI API Errors**
   - Verify API key is valid and has sufficient credits
   - Check rate limits and quotas
   - Ensure model name is correct

### Getting Help

- 📖 Check the individual README files in each folder
- 🐛 Open an issue on GitHub
- 💬 Join our community discussions

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/)
- UI powered by [Streamlit](https://streamlit.io/)
- API built with [FastAPI](https://fastapi.tiangolo.com/)
- Containerized with [Docker](https://docker.com/)
