# Solution Description

We propose building a parliamentary voting simulator based on a multi-agent system built using LangGraph, reflecting democratic processes in an interactive and realistic way.

## Key Components of the Solution

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

## Technologies Used

- **LangGraph** – builds the agent and process flow graph
- **LangChain Agents & Tools** – knowledge retrieval, multi-agent system
- **Wikipedia API / RAG** – pulls data from external sources
- **Vector Databases** – e.g., FAISS
- **LangSmith** – agent tracking, versioning, and monitoring
- **Streamlit** – user interface
- **Docker** – one-command deployment

## Goal

To create a democratic, transparent, and interactive model simulating parliamentary voting, which can serve as:

- An educational tool
- A prototype for modern civic engagement systems
- An inspiration for applying GenAI to model socio-political processes
