import asyncio
import json
import os
from mcp_server import scrape_github, analyze_profile, generate_card_html

async def test_end_to_end():
    username = "torvalds"
    print(f"--- Step 1: Scrapping GitHub for {username} ---")
    try:
        github_data = await scrape_github(username)
        if "error" in github_data:
            print(f"Error in scrape_github: {github_data['error']}")
            return
        print("Scrape successful.")
    except Exception as e:
        print(f"Failed to scrape_github: {e}")
        return

    print(f"\n--- Step 2: Analyzing profile for {username} ---")
    try:
        analysis = await analyze_profile(github_data)
        print("Analysis successful.")
    except Exception as e:
        print(f"Failed to analyze_profile: {e}")
        return

    print(f"\n--- Step 3: Generating card HTML ---")
    try:
        html = await generate_card_html(username, github_data, analysis)
        print("HTML generation successful.")
    except Exception as e:
        print(f"Failed to generate_card_html: {e}")
        return

    print(f"\n--- Results ---")
    print(f"Card Theme: {analysis.get('card_theme')}")
    print(f"Developer Vibe: {analysis.get('developer_vibe')}")
    
    # Verify HTML isn't empty
    if html:
        print("\nEnd-to-end test passed successfully!")

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
