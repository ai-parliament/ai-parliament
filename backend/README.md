# Backend API 🔧

The backend module provides a FastAPI-based REST API that serves as the bridge between the frontend interface and the AI simulation engine. It handles HTTP requests, manages simulation state, and orchestrates the AI agents.

## 🏗️ Architecture

The backend follows a clean API architecture:

```
FastAPI Application
├── API Routes (routes.py)
├── AI Service Integration (ai_service.py)
├── Request/Response Models
└── CORS & Middleware
```

## 📁 Structure

```
backend/
├── 📄 Dockerfile                 # Container configuration
├── 📄 pyproject.toml             # Module configuration
├── 📄 requirements.txt           # Dependencies
├── 📄 run_simulation.py          # Standalone simulation runner
├── 📄 README.md                  # This documentation
└── 📁 src/
    ├── 📄 main.py                # FastAPI application entry point
    └── 📁 api/
        ├── ai_service.py         # AI module integration service
        └── routes.py             # API endpoints and routing
```

## 🚀 API Endpoints

### Health Check
- **GET** `/api/health`
- Returns service health status
- Used for Docker health checks

### Simulation Management

#### Create Simulation
- **POST** `/api/create_simulation`
- Creates a new parliamentary simulation
- **Request Body:**
  ```json
  {
    "party_names": ["Party A", "Party B"],
    "party_abbreviations": ["PA", "PB"],
    "politicians_per_party": {
      "Party A": [
        {"name": "John Doe", "role": "Leader"},
        {"name": "Jane Smith", "role": "Member"}
      ]
    },
    "llm_config": {
      "model_name": "gpt-4o-mini",
      "temperature": 0.7,
      "max_tokens": 2000
    }
  }
  ```
- **Response:**
  ```json
  {
    "message": "Simulation created successfully",
    "parties": [
      {
        "name": "Party A",
        "acronym": "PA",
        "politicians": [...]
      }
    ]
  }
  ```

#### Generate Legislation
- **POST** `/api/generate_legislation`
- Generates detailed legislation from a topic
- **Request Body:**
  ```json
  {
    "topic": "Climate Change Action",
    "llm_config": {
      "model_name": "gpt-4o-mini",
      "temperature": 0.7,
      "max_tokens": 2000
    }
  }
  ```
- **Response:**
  ```json
  {
    "legislation_text": "Detailed legislation text..."
  }
  ```

#### Run Intra-Party Deliberation
- **POST** `/api/run_intra_party_deliberation`
- Executes internal party discussions
- **Request Body:**
  ```json
  {
    "legislation_text": "The proposed legislation...",
    "llm_config": {...}
  }
  ```
- **Response:**
  ```json
  {
    "results": {
      "Party A": {
        "discussion": "Internal discussion summary...",
        "position": "Party position on the legislation"
      }
    }
  }
  ```

#### Run Inter-Party Debate
- **POST** `/api/run_inter_party_debate`
- Facilitates debates between parties
- **Request Body:**
  ```json
  {
    "legislation_text": "The proposed legislation...",
    "intra_party_results": {...},
    "llm_config": {...}
  }
  ```

#### Conduct Final Voting
- **POST** `/api/conduct_final_voting`
- Executes the final parliamentary vote
- **Request Body:**
  ```json
  {
    "legislation_text": "The proposed legislation...",
    "inter_party_results": {...},
    "llm_config": {...}
  }
  ```

#### Generate Summary
- **POST** `/api/generate_summary`
- Creates a comprehensive simulation summary
- **Request Body:**
  ```json
  {
    "legislation_text": "The proposed legislation...",
    "voting_results": {...},
    "llm_config": {...}
  }
  ```

## 🔧 Core Components

### FastAPI Application (`main.py`)

Main application entry point:
- FastAPI app initialization
- CORS middleware configuration
- Environment variable loading
- Server startup configuration

**Key Features:**
- Automatic environment variable loading
- CORS support for frontend integration
- Configurable port (default: 8000)
- Development mode with auto-reload

### API Routes (`routes.py`)

Defines all API endpoints:
- Request/response models using Pydantic
- Route handlers for each endpoint
- Error handling and validation
- AI service integration

**Request Models:**
- `SimulationCreateRequest`
- `GenerateLegislationRequest`
- `IntraPartyDeliberationRequest`
- `InterPartyDebateRequest`
- `FinalVotingRequest`
- `GenerateSummaryRequest`

### AI Service Integration (`ai_service.py`)

Bridges the API and AI module:
- AI agent initialization
- Simulation orchestration
- State management
- Result processing

**Key Methods:**
- `create_simulation()`: Initialize parties and politicians
- `generate_legislation()`: Create legislation from topic
- `run_intra_party_deliberation()`: Manage internal discussions
- `run_inter_party_debate()`: Facilitate cross-party debates
- `conduct_final_voting()`: Execute voting process
- `generate_summary()`: Compile final results

## 🐳 Docker Configuration

### Dockerfile Features

- **Base Image**: Python 3.11 slim
- **Multi-stage copying**: Efficient layer management
- **Dependency installation**: Backend + AI requirements
- **Directory structure**: Organized code layout
- **Environment variables**: Runtime configuration
- **Port exposure**: 8000 for API access

### Build Process

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Copy and install dependencies
COPY backend/requirements.txt /app/backend-requirements.txt
COPY ai/requirements.txt /app/ai-requirements.txt
RUN pip install --no-cache-dir -r /app/backend-requirements.txt -r /app/ai-requirements.txt

# Copy application code
COPY backend/src/ /app/src/
COPY ai/src/ /app/src/ai/

# Configure and start
EXPOSE 8000
ENV PYTHONPATH=/app
CMD ["python", "-m", "src.main"]
```

## 📋 Dependencies

### Core Dependencies
- **FastAPI**: Modern web framework for APIs
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation and serialization
- **python-dotenv**: Environment variable management

### AI Integration
- **LangChain**: AI agent framework
- **LangGraph**: Multi-agent orchestration
- **OpenAI**: Language model integration
- **LangSmith**: Monitoring and tracing

### Data Processing
- **FAISS**: Vector database
- **Wikipedia**: Knowledge retrieval
- **PyYAML**: Configuration management

## 🚀 Usage

### Development Mode

```bash
cd backend
pip install -r requirements.txt
python -m src.main
```

The server will start on `http://localhost:8000` with auto-reload enabled.

### Production Mode

```bash
# Using Docker
docker build -t ai-parliament-backend .
docker run -p 8000:8000 --env-file .env ai-parliament-backend

# Using Docker Compose
docker-compose up backend
```

### Standalone Simulation

For testing without the API:

```bash
cd backend
python run_simulation.py
```

## ⚙️ Configuration

### Environment Variables

Required variables:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
GPT_MODEL_NAME=gpt-4o-mini

# Server Configuration
PORT=8000
PYTHONPATH=/app

# Optional: LangSmith Monitoring
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=ai-parliament
LANGSMITH_TRACING=true
```

### CORS Configuration

The API is configured to allow cross-origin requests:
- **Origins**: `["*"]` (should be restricted in production)
- **Methods**: All HTTP methods
- **Headers**: All headers
- **Credentials**: Enabled

## 🧪 Testing

### Manual API Testing

Using curl:
```bash
# Health check
curl http://localhost:8000/api/health

# Create simulation
curl -X POST http://localhost:8000/api/create_simulation \
  -H "Content-Type: application/json" \
  -d '{"party_names": ["Test Party"], "politicians_per_party": {...}}'
```

Using Python requests:
```python
import requests

# Test health endpoint
response = requests.get("http://localhost:8000/api/health")
print(response.json())

# Test simulation creation
data = {
    "party_names": ["Progressive Party"],
    "politicians_per_party": {
        "Progressive Party": [
            {"name": "Alice Johnson", "role": "Leader"}
        ]
    }
}
response = requests.post("http://localhost:8000/api/create_simulation", json=data)
print(response.json())
```

### Automated Testing

```bash
cd backend
python -m pytest tests/
```

## 🔍 API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   # Kill the process
   kill -9 <PID>
   ```

2. **Environment Variables Not Loading**
   - Ensure `.env` file is in the project root
   - Check file permissions
   - Verify variable names and values

3. **AI Service Initialization Errors**
   - Verify OpenAI API key
   - Check model availability
   - Monitor API rate limits

4. **CORS Issues**
   - Check frontend URL configuration
   - Verify CORS middleware setup
   - Test with browser developer tools

### Performance Optimization

- **Async Operations**: Use FastAPI's async capabilities
- **Connection Pooling**: Implement for database connections
- **Caching**: Cache frequent AI responses
- **Rate Limiting**: Implement to prevent abuse

### Monitoring

- **Health Checks**: Use `/api/health` endpoint
- **Logging**: Implement structured logging
- **Metrics**: Monitor response times and error rates
- **LangSmith**: Use for AI agent monitoring

## 📚 Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)