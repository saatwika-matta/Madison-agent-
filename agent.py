"""
agent.py — Madison Agent
Core agentic loop: sends tasks to Claude, handles tool use autonomously,
and returns structured JSON output.
"""

import json
import anthropic
from tools import TOOL_DEFINITIONS, TOOL_MAP

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are Madison, an autonomous enterprise data extraction agent.

Your job is to extract structured intelligence from GitHub's REST API for a given username.

Always follow this sequence:
1. Call get_github_user to fetch the user's profile.
2. Call get_user_repos to fetch their top repositories.
3. Call get_repo_details on their most starred repository.

After all tool calls are complete, return ONLY a valid JSON object — 
no markdown fences, no preamble, no explanation. Just raw JSON.

JSON structure:
{
  "username": "string",
  "profile": {
    "login": "string",
    "name": "string or null",
    "bio": "string or null",
    "company": "string or null",
    "location": "string or null",
    "public_repos": number,
    "followers": number,
    "following": number,
    "created_at": "string"
  },
  "top_repos": [
    {
      "name": "string",
      "description": "string or null",
      "stars": number,
      "forks": number,
      "language": "string or null",
      "topics": [],
      "updated_at": "string"
    }
  ],
  "featured_repo": {
    "name": "string",
    "full_name": "string",
    "description": "string or null",
    "stars": number,
    "forks": number,
    "open_issues": number,
    "language": "string or null",
    "default_branch": "string",
    "created_at": "string",
    "updated_at": "string",
    "homepage": "string or null"
  },
  "summary": "2-3 sentence professional summary of this developer"
}"""


def process_tool_calls(response_content: list) -> list[dict]:
    tool_results = []
    for block in response_content:
        if block.type != "tool_use":
            continue
        tool_fn = TOOL_MAP.get(block.name)
        if not tool_fn:
            result = {"error": f"Unknown tool: {block.name}"}
        else:
            try:
                result = tool_fn(**block.input)
            except Exception as e:
                result = {"error": f"Tool execution failed: {str(e)}"}
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": json.dumps(result)
        })
    return tool_results


def extract_final_json(response_content: list) -> dict:
    for block in response_content:
        if block.type == "text" and block.text.strip():
            text = block.text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1]).strip()
            # Find JSON object in the text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                text = text[start:end]
            return json.loads(text)
    raise ValueError(f"No text block found. Blocks: {[b.type for b in response_content]}")


def run_agent(username: str) -> dict:
    messages = [
        {
            "role": "user",
            "content": f"Extract a complete intelligence profile for GitHub user: {username}"
        }
    ]

    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages
        )

        messages.append({
            "role": "assistant",
            "content": response.content
        })

        if response.stop_reason == "end_turn":
            return extract_final_json(response.content)

        if response.stop_reason == "tool_use":
            tool_results = process_tool_calls(response.content)
            messages.append({
                "role": "user",
                "content": tool_results
            })
            continue

        raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason}")

    raise RuntimeError(f"Agent did not complete within {max_iterations} iterations.")