import os
import json
from collections import Counter
from typing import Dict, List

import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp.server.fastmcp import FastMCP

# Environment

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Clients

client = genai.Client(api_key=GEMINI_API_KEY)
mcp = FastMCP("GitHub Dev Card MCP Server")

# Tool 1: scrape_github

@mcp.tool()
async def scrape_github(username: str) -> Dict:
    """
    Fetch GitHub profile information and repositories.
    Returns:
    - name
    - bio
    - location
    - public_repos
    - followers
    - avatar_url
    - top 6 repos
    - aggregated languages
    """
    headers = {
        "Accept": "application/vnd.github+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as http_client:

        # Fetch User Profile

        user_response = await http_client.get(
            f"https://api.github.com/users/{username}"
        )
        if user_response.status_code != 200:
            return {
                "error": f"GitHub user '{username}' not found"
            }
        user_data = user_response.json()

        # Fetch Repositories

        repos_response = await http_client.get(
            f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
        )
        repos_data = []
        if repos_response.status_code == 200:
            repos_data = repos_response.json()

        # Aggregate Languages

        language_counter = Counter()
        for repo in repos_data:
            language = repo.get("language")

            if language:
                language_counter[language] += 1

        # Top 6 Repositories

        sorted_repos = sorted(
            repos_data,
            key=lambda repo: repo.get("stargazers_count", 0),
            reverse=True,
        )[:6]

        top_repos = []
        for repo in sorted_repos:
            top_repos.append({
                "name": repo.get("name"),
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language"),
                "description": repo.get("description"),
            })

        # Final Result

        return {
            "name": user_data.get("name") or username,
            "bio": user_data.get("bio"),
            "location": user_data.get("location"),
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
            "avatar_url": user_data.get("avatar_url"),
            "top_repos": top_repos,
            "most_used_languages": dict(language_counter),
        }

# Tool 2: analyze_profile

@mcp.tool()
async def analyze_profile(github_data: Dict) -> Dict:
    """
    Analyze a GitHub profile using Gemini 2.5 Flash.
    Returns:
    - developer_vibe
    - top_skills
    - fun_fact
    - card_theme
    """
    prompt = f"""
You are analyzing a GitHub developer profile.

GitHub Data:
{json.dumps(github_data, indent=2)}

Return ONLY valid JSON in this exact format:
{{
  "developer_vibe": "1 sentence personality",
  "top_skills": ["skill1", "skill2", "skill3"],
  "fun_fact": "something clever inferred from their repos",
  "card_theme": "hacker"
}}

Allowed card_theme values:
- hacker
- builder
- researcher
- designer
- open-source-hero
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )

    try:
        return json.loads(response.text)
    except Exception:
        return {
            "developer_vibe": "A passionate open-source developer.",
            "top_skills": ["Python", "Git", "Open Source"],
            "fun_fact": "Loves building cool things on GitHub.",
            "card_theme": "builder",
        }

# Tool 3: generate_card_html

@mcp.tool()
async def generate_card_html(
    username: str,
    github_data: Dict,
    analysis: Dict,
) -> str:
    """
    Generate a self-contained HTML dev card.
    """
    theme = analysis.get("card_theme", "builder")
    theme_styles = {
        "hacker": {
            "background": "#0d1117",
            "text": "#58a6ff",
            "accent": "#238636",
        },
        "builder": {
            "background": "#ffffff",
            "text": "#24292f",
            "accent": "#0969da",
        },
        "researcher": {
            "background": "#f6f8fa",
            "text": "#1f2328",
            "accent": "#8250df",
        },
        "designer": {
            "background": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
            "text": "#222222",
            "accent": "#d63384",
        },
        "open-source-hero": {
            "background": "#238636",
            "text": "#ffffff",
            "accent": "#2ea043",
        },
    }
    style = theme_styles.get(theme, theme_styles["builder"])
    skills_html = ""
    for skill in analysis.get("top_skills", []):
        skills_html += f"""
        <span
            style="
                display:inline-block;
                margin:4px;
                padding:6px 12px;
                border-radius:999px;
                background:rgba(255,255,255,0.15);
                font-size:12px;
                font-weight:600;
            "
        >
            {skill}
        </span>
        """
    # Repositories
    repos_html = ""

    for repo in github_data.get("top_repos", [])[:3]:
        repos_html += f"""
        <div
            style="
                margin-top:10px;
                padding:10px;
                border-radius:10px;
                background:rgba(255,255,255,0.08);
            "
        >
            <div style="font-weight:700;">
                {repo.get("name")}
            </div>

            <div style="font-size:13px; opacity:0.85;">
                ⭐ {repo.get("stars")} • {repo.get("language")}
            </div>

            <div style="font-size:12px; margin-top:4px;">
                {repo.get("description") or ""}
            </div>
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <title>{username} Dev Card</title>
</head>

<body
    style="
        margin:0;
        padding:40px;
        background:#111827;
        display:flex;
        justify-content:center;
        align-items:center;
        min-height:100vh;
        font-family:Inter,Arial,sans-serif;
    "
>

<div
    style="
        width:420px;
        border-radius:24px;
        padding:28px;
        background:{style["background"]};
        color:{style["text"]};
        box-shadow:0 10px 40px rgba(0,0,0,0.25);
    "
>

    <div
        style="
            display:flex;
            align-items:center;
            gap:18px;
        "
    >
        <img
            src="{github_data.get("avatar_url")}"
            alt="avatar"
            style="
                width:90px;
                height:90px;
                border-radius:50%;
                border:4px solid {style["accent"]};
            "
        />

        <div>
            <h1 style="margin:0; font-size:28px;">
                {github_data.get("name")}
            </h1>

            <p style="margin:4px 0 0 0; opacity:0.8;">
                @{username}
            </p>
        </div>
    </div>

    <p
        style="
            margin-top:24px;
            font-size:16px;
            line-height:1.6;
            font-style:italic;
        "
    >
        "{analysis.get("developer_vibe")}"
    </p>

    <div style="margin-top:18px;">
        {skills_html}
    </div>

    <div
        style="
            display:flex;
            gap:24px;
            margin-top:24px;
            font-size:15px;
            font-weight:600;
        "
    >
        <span>
            📦 {github_data.get("public_repos")} repos
        </span>

        <span>
            👥 {github_data.get("followers")} followers
        </span>
    </div>

    <div style="margin-top:28px;">
        <h2 style="margin-bottom:12px;">
            Top Repositories
        </h2>

        {repos_html}
    </div>

    <div
        style="
            margin-top:28px;
            padding:14px;
            border-radius:14px;
            background:rgba(255,255,255,0.08);
            font-size:14px;
        "
    >
        💡 {analysis.get("fun_fact")}
    </div>
</div>
</body>
</html>
"""
    return html

# Tool 4: save_card

@mcp.tool()
async def save_card(username: str, html: str) -> str:
    """
    Save generated card HTML.
    """
    cards_dir = os.path.join("static", "cards")
    os.makedirs(cards_dir, exist_ok=True)
    file_path = os.path.join(cards_dir, f"{username}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    return f"/static/cards/{username}.html"

# Run MCP Server

if __name__ == "__main__":
    mcp.run()