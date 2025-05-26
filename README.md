# AI Parliament

AI Parliament is a simulation of a parliamentary system where agents representing political parties and politicians collaborate, debate, and decide on legislative proposals. The system integrates Wikipedia-based knowledge, graph databases, and multi-agent interactions to simulate the decision-making process.

## Project Structure

    ```
    ai-parliament/
    ├── ai/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── src/
    │   │   ├── __init__.py
    │   │   ├── config/
    │   │   │   └── config_manager.py
    │   │   ├── agents/
    │   │   │   ├── main_agent.py           # Manages all other agents
    │   │   │   ├── party_agent.py          # Represents a political party
    │   │   │   ├── politician_agent.py     # Represents individual politicians
    │   │   │   └── wiki_agent.py           # Searches Wikipedia for party and politician data
    │   │   ├── database/
    │   │   │   └── graph_database.py       # Handles graph database integration
    │   │   └── simulation/
    │   │       ├── party_discussion.py     # Simulates discussions within a party
    │   │       ├── inter_party_debate.py   # Simulates debates between parties
    │   │       └── voting_system.py        # Determines if the legislation passes
    ├── backend/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── src/
    │   │   ├── __init__.py
    │   │   ├── config/
    │   │   │   └── config_manager.py
    │   │   └── api/
    │   │       ├── endpoints.py            # API endpoints for interacting with the system
    │   │       └── models.py               # Data models for API
    ├── frontend/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   ├── src/
    │   │   ├── __init__.py
    │   │   ├── components/
    │   │   │   ├── party_selector.py       # UI for selecting parties
    │   │   │   ├── politician_selector.py  # UI for selecting politicians
    │   │   │   └── results_display.py      # Displays the final results
    │   │   └── app.py                      # Main frontend application
    ├── [docker-compose.yml]                # Docker configuration for the entire system
    ├── [.env.shared]                       # Shared environment variables
    ├── [.env.secret]                       # Secret environment variables
    ├── .gitignore                          # Git ignore file
    └── [README.md]                         # Project documentation
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

## Project Setup

### Manual Setup

1. Navigate to the root of your project:

    ```bash
    cd /Users/mchojna/Documents/Repozytoria/ai-parliament
    ```

2. Create virtual environments for each subproject (`ai`, `backend`, `frontend`) using `uv`:

    ```bash
    cd ai
    uv venv .venv
    cd ../backend
    uv venv .venv
    cd ../frontend
    uv venv .venv
    ```

3. Activate the virtual environment for any subproject when needed:

    ```bash
    source .venv/bin/activate
    ```

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

### Automated Setup Script

Run the `setup.sh` script to automate the creation of virtual environments:

1. Make the script executable:

    ```bash
    chmod +x [setup.sh](http://_vscodecontentref_/7)
    ```

2. Run the script:

    ```bash
    [setup.sh](http://_vscodecontentref_/8)
    ```

This will create virtual environments for the `ai`, `backend`, and `frontend` subprojects.

3. Activate the virtual environment for any subproject when needed:

    ```bash
    source .venv/bin/activate
    ```
4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```
