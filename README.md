# GitHub Dev Card Generator 

An AI-powered GitHub profile card generator built using **Google ADK**, **Gemini 2.5 Flash**, **FastAPI**, and **MCP (Model Context Protocol)**.

This project analyzes any public GitHub profile, extracts developer insights using Gemini, and generates a beautiful personalized developer card.

---

# Features

- Scrapes public GitHub profiles using GitHub REST API
- Uses Gemini 2.5 Flash for AI-powered profile analysis
- MCP-based tool orchestration with Google ADK
- Generates beautiful developer cards dynamically
- FastAPI backend with async ADK Runner
- Frontend integration for instant card generation
- Saves generated cards as static HTML pages
- Ready for Cloud Run / Docker deployment

---

# Tech Stack

## Backend
- Python 3.11
- FastAPI
- Google ADK
- MCP (FastMCP)
- Gemini 2.5 Flash
- Uvicorn

## Frontend
- React / Vite
- TailwindCSS

## APIs
- GitHub REST API
- Gemini API

---

# Project Structure

```bash
github-card-generator/
│
├── backend/
│   ├── agent.py
│   ├── main.py
│   ├── mcp_server.py
│   ├── requirements.txt
│   ├── static/
│   │   └── cards/
│   └── .env
│
├── frontend/
│
├── docker-compose.yml
└── README.md
```

---

# Architecture Overview

## MCP Server (`mcp_server.py`)

Implemented a FastMCP server with 4 custom tools:

### 1. `scrape_github(username)`
Fetches:
- profile info
- followers
- repo count
- top repositories
- most-used languages

### 2. `analyze_profile(github_data)`
Uses Gemini 2.5 Flash to generate:
- developer vibe
- top skills
- fun fact
- card theme

### 3. `generate_card_html(...)`
Creates a complete responsive HTML developer card.

### 4. `save_card(username, html)`
Saves the generated HTML into:

```bash
static/cards/{username}.html
```

---

## ADK Agent (`agent.py`)

Created an ADK agent named:

```python
github_card_agent
```

The agent:
- uses Gemini 2.5 Flash
- connects to MCP tools through `McpToolset`
- orchestrates the entire workflow automatically

### Agent Workflow

```text
scrape_github
    ↓
analyze_profile
    ↓
generate_card_html
    ↓
save_card
```

---

## FastAPI Backend (`main.py`)

Implemented:
- ADK Runner
- InMemorySessionService
- InMemoryMemoryService
- async event streaming

### API Endpoints

| Endpoint | Description |
|---|---|
| `POST /generate` | Generates developer card |
| `GET /card/{username}` | Serves saved card |
| `GET /health` | Health check |

---

# Environment Setup

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/github-card-generator.git
cd github-card-generator
```

---

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

### Windows
```bash
.venv\Scripts\activate
```

### Mac/Linux
```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

## 4. Configure Environment Variables

Create `.env` inside `backend/`

```env
GOOGLE_API_KEY=your_google_api_key
GITHUB_TOKEN=your_github_token
```

---

# Running the Project

## Start Backend

```bash
cd backend

uvicorn main:app --host 0.0.0.0 --port 8080
```

> Avoid using `--reload` with MCP on Windows due to async transport instability.

---

## Start Frontend

```bash
cd frontend

npm install
npm run dev
```

---

# Testing

## Test MCP Tools

```bash
python test_mcp.py
```

## Test ADK Agent

```bash
python test_agent.py
```

---

# Example Generated Card

Features:
- Developer vibe summary
- Top skills badges
- Top repositories
- Followers & repo stats
- Dynamic themes

Supported themes:
- hacker
- builder
- researcher
- designer
- open-source-hero

---

# Deployment

Prepared for:
- Docker
- Google Cloud Run
- Railway
- Render
