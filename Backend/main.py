import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types

from agent import github_card_agent

app = FastAPI(title="GitHub Dev Card Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
CARDS_DIR = STATIC_DIR / "cards"

CARDS_DIR.mkdir(parents=True, exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ADK Services

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

runner = Runner(
    app_name="github_card_app",
    agent=github_card_agent,
    session_service=session_service,
    memory_service=memory_service,
)

# Request Model

class GenerateRequest(BaseModel):
    username: str

# Health Check

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Generate Endpoint

@app.post("/generate")
async def generate(request: GenerateRequest):
    username = request.username.strip()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username is required",
        )

    session_id = f"session_{username}"
    user_id = username

    try:
        existing_session = await session_service.get_session(
            app_name="github_card_app",
            user_id=user_id,
            session_id=session_id,
        )
        if not existing_session:
            await session_service.create_session(
                app_name="github_card_app",
                user_id=user_id,
                session_id=session_id,
            )

        # Run Agent

        final_response = ""

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[
                    types.Part(
                        text=f"Generate a dev card for {username}"
                    )
                ],
            ),
        ):
            try:
                if (
                    hasattr(event, "model_response")
                    and event.model_response
                    and hasattr(event.model_response, "text")
                ):
                    final_response = event.model_response.text
            except Exception:
                pass

        # Verify Card Exists

        card_file = CARDS_DIR / f"{username}.html"
        if not card_file.exists():
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Card file not found for {username}. "
                    f"Agent response: {final_response}"
                ),
            )

        # Read Generated HTML

        with open(card_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Success Response

        return {
            "success": True,
            "username": username,
            "message": final_response,
            "card_url": f"/static/cards/{username}.html",
            "html": html_content,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

# Serve Generated Cards

@app.get("/card/{username}")
async def get_card(username: str):
    file_path = CARDS_DIR / f"{username}.html"
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Card not found",
        )
    return FileResponse(file_path)

# Local Development Entry Point

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )