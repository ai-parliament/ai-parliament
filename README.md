# AI Parliament

AI Parliament is a simulation of a parliamentary system where agents representing political parties and politicians collaborate, debate, and decide on legislative proposals. The system integrates Wikipedia-based knowledge, graph databases, and multi-agent interactions to simulate the decision-making process.

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

## Project Structure

    ```
    ai-parliament/
    ├── ai/
    │   ├── Dockerfile
    │   ├── src/
    │   │   ├── __init__.py
    │   │   ├── agents/
    │   │   │   ├── main_agent.py           # Manages all other agents
    │   │   │   ├── party_agent.py          # Represents a political party
    │   │   │   ├── politician_agent.py     # Represents individual politicians
    │   │   │   └── wiki_agent.py           # Searches Wikipedia for party and politician data
    │   │   ├── database/
    │   │   │   └── vector_database.py      # Handles vector database integration
    │   │   └── simulation/
    │   │       ├── party_discussion.py     # Simulates discussions within a party
    │   │       ├── inter_party_debate.py   # Simulates debates between parties
    │   │       └── voting_system.py        # Determines if the legislation passes
    ├── backend/
    │   ├── Dockerfile
    │   ├── src/
    │   │   ├── __init__.py
    │   │   └── api/
    │   │       ├── endpoints.py            # API endpoints for interacting with the system
    │   │       └── models.py               # Data models for API
    ├── frontend/
    │   ├── Dockerfile
    │   ├── src/
    │   │   ├── __init__.py
    │   │   ├── components/
    │   │   │   ├── party_selector.py       # UI for selecting parties
    │   │   │   ├── politician_selector.py  # UI for selecting politicians
    │   │   │   └── results_display.py      # Displays the final results
    │   │   └── app.py                      # Main frontend application
    ├── docker-compose.yml                  # Docker configuration for the entire system
    ├── .env.shared                         # Shared environment variables
    ├── .env.secret                         # Secret environment variables
    ├── .gitignore                          # Git ignore file
    └── README.md                           # Project documentation
    ```

## Prerequisites

- Ensure you have Python 3.11 installed. You can check your Python version with:

    ```bash
    python --version
    ```

- Install `uv` for managing virtual environments:

    ```bash
    pip install uv
    ```

## Running the Application

### Using Docker Compose (Recommended)

1. Make sure you have Docker and Docker Compose installed:

    ```bash
    docker --version
    docker-compose --version
    ```

2. Build and start the containers:

    ```bash
    docker-compose up --build
    ```

3. Access the application:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000/api

4. To stop the application:

    ```bash
    docker-compose down
    ```

### Running Locally (Development)

#### Backend

1. Navigate to the backend directory:

    ```bash
    cd backend
    ```

2. Create requirements.txt (if not already created):

    ```bash
    echo "fastapi>=0.95.0" > requirements.txt
    echo "uvicorn>=0.22.0" >> requirements.txt
    echo "python-dotenv>=1.0.0" >> requirements.txt
    ```

3. Install dependencies:

    ```bash
    uv pip install -r requirements.txt
    ```

4. Run the backend server:

    ```bash
    python -m src.main
    ```

#### Frontend

1. Navigate to the frontend directory:

    ```bash
    cd frontend
    ```

2. Create requirements.txt (if not already created):

    ```bash
    echo "streamlit>=1.29.0" > requirements.txt
    echo "requests>=2.31.0" >> requirements.txt
    ```

3. Install dependencies:

    ```bash
    uv pip install -r requirements.txt
    ```

4. Run the Streamlit app:

    ```bash
    streamlit run src/app.py
    ```
