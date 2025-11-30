
# Customer Support Agent

An autonomous customer support agent built with Python, OpenAI, and Chainlit. The agent leverages OpenAI's function calling capabilities to intelligently handle customer queries, check order statuses, and escalate issues when necessary, all within a modular Client-Server architecture.

## Features

- **Autonomous Agent**: Uses OpenAI's GPT-4.1 mini to understand and resolve user queries.
- **Tool Usage**: Can fetch order status from a mock database and escalate issues.
- **Guardrails**: Prevents the agent from answering off-topic questions (e.g., coding, math).
- **Observability**: Logs token usage and latency for every agent execution.
- **Modern UI**: Built with Chainlit for a chat-like experience.

## Architecture

The application follows a Client-Server architecture where the Chainlit frontend communicates with a FastAPI backend. The backend orchestrates the AI agent, which interacts with OpenAI and executes tools.

```mermaid
graph TD
    subgraph Client
        User[User] -->|Interacts| UI[Chainlit Frontend]
    end

    subgraph Server
        UI -->|HTTP POST /chat| API[FastAPI Backend]
        API -->|Messages| Agent[Agent Orchestrator]
        Agent -->|Prompt| LLM[OpenAI gpt-4.1-mini]
        LLM -->|Tool Call?| Agent
        Agent -->|Yes| Tools[Tool Execution]
        Tools -->|Result| Agent
        Agent -->|Result + History| LLM
        LLM -->|Final Response| Agent
        Agent -->|Response| API
    end

    API -->|JSON| UI
    UI -->|Display| User
```

## Project Structure

```
cloudstok-assignment/
├── src/
│   ├── agents/
│   │   ├── agent.py       # Core Agent logic (OpenAI interaction loop)
│   │   └── prompts.py     # System prompts and guardrail definitions
│   ├── tools/
│   │   └── tools.py       # Mock tools (get_order_status, escalate_to_human)
│   ├── schemas/
│   │   └── models.py      # Pydantic models for data validation
│   └── helpers/
│       └── utils.py       # Utility functions (logging, decorators)
├── main.py                # FastAPI Backend entry point
├── app.py                 # Chainlit Frontend entry point
├── docker-compose.yml     # Multi-container orchestration
├── Dockerfile             # Docker image definition
├── pyproject.toml         # Project dependencies and configuration
├── uv.lock                # Dependency lock file
├── .env                   # Environment variables (API keys)
└── README.md              # Project documentation
```

## Setup

1.  **Clone the repository**
```bash
git clone https://github.com/suryanshgupta9933/cloudstok-assignment.git
cd cloudstok-assignment
```
2.  **Create a virtual environment and install dependencies using uv**:
```bash
pip install uv

# Create virtual environment
uv venv

# Activate virtual environment
# On Windows
.venv\Scripts\activate
# On Linux/Mac
source .venv/bin/activate

# Install dependencies
uv sync
```
3.  **Configure Environment**:
    - Copy `.env.example` to `.env`
    - Add your `OPENAI_API_KEY`

## Usage

### Run with Docker Compose (Recommended)
This will start both the Backend (port 8000) and Frontend (port 8001).

```bash
docker-compose up --build
```

Access the UI at: `http://localhost:8001`

### Run Locally (Manual)
You need two terminals:

1.  **Start Backend**:
    ```bash
    uv run uvicorn main:app
    ```
2.  **Start Frontend**:
    ```bash
    uv run chainlit run app.py
    ```

### API Usage

You can interact with the backend API directly using `curl` or any HTTP client.

**Endpoint**: `POST http://localhost:8000/chat`

**Request Body**:
```json
{
  "messages": [
    {"role": "user", "content": "Where is my order 123?"}
  ]
}
```

**Example (curl)**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

## Demo Video
https://github.com/user-attachments/assets/c779b594-174f-4d22-8375-c66db74dbbbe

