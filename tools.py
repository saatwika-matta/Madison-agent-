"""
tools.py — Madison Agent
Tool implementations: GitHub REST API calls with retry logic.
Each function is registered as a Claude tool in agent.py.
"""

import time
import httpx
from typing import Any

GITHUB_BASE = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github.v3+json"}


def fetch_with_retry(url: str, max_retries: int = 3) -> Any:
    for attempt in range(max_retries):
        try:
            response = httpx.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 404:
                return {"error": f"Not found: {url}"}
            if 400 <= response.status_code < 500:
                return {"error": f"Client error {response.status_code}: {response.text}"}
            response.raise_for_status()
            return response.json()
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            if attempt == max_retries - 1:
                return {"error": f"Network error after {max_retries} retries: {str(e)}"}
            time.sleep(2 ** attempt)
        except httpx.HTTPStatusError as e:
            if attempt == max_retries - 1:
                return {"error": f"HTTP error after {max_retries} retries: {str(e)}"}
            time.sleep(2 ** attempt)
    return {"error": "Max retries exceeded"}


def get_github_user(username: str) -> dict:
    data = fetch_with_retry(f"{GITHUB_BASE}/users/{username}")
    if "error" in data:
        return data
    return {
        "login":        data.get("login"),
        "name":         data.get("name"),
        "bio":          data.get("bio"),
        "company":      data.get("company"),
        "location":     data.get("location"),
        "public_repos": data.get("public_repos"),
        "followers":    data.get("followers"),
        "following":    data.get("following"),
        "created_at":   data.get("created_at"),
    }


def get_user_repos(username: str) -> list:
    data = fetch_with_retry(
        f"{GITHUB_BASE}/users/{username}/repos?sort=stargazers&per_page=5&type=owner"
    )
    if isinstance(data, dict) and "error" in data:
        return [data]
    return [
        {
            "name":        r.get("name"),
            "description": r.get("description"),
            "stars":       r.get("stargazers_count"),
            "forks":       r.get("forks_count"),
            "language":    r.get("language"),
            "topics":      r.get("topics", []),
            "updated_at":  r.get("updated_at"),
        }
        for r in data
    ]


def get_repo_details(username: str, repo: str) -> dict:
    data = fetch_with_retry(f"{GITHUB_BASE}/repos/{username}/{repo}")
    if "error" in data:
        return data
    return {
        "name":           data.get("name"),
        "full_name":      data.get("full_name"),
        "description":    data.get("description"),
        "stars":          data.get("stargazers_count"),
        "forks":          data.get("forks_count"),
        "open_issues":    data.get("open_issues_count"),
        "language":       data.get("language"),
        "default_branch": data.get("default_branch"),
        "created_at":     data.get("created_at"),
        "updated_at":     data.get("updated_at"),
        "homepage":       data.get("homepage"),
    }


TOOL_MAP = {
    "get_github_user":  get_github_user,
    "get_user_repos":   get_user_repos,
    "get_repo_details": get_repo_details,
}

TOOL_DEFINITIONS = [
    {
        "name": "get_github_user",
        "description": "Fetch a GitHub user's public profile including name, bio, company, location, follower count, and total public repository count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "The GitHub username to look up."}
            },
            "required": ["username"]
        }
    },
    {
        "name": "get_user_repos",
        "description": "Fetch the top 5 public repositories owned by a GitHub user, sorted by star count.",
        "input_schema": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "The GitHub username whose repos to list."}
            },
            "required": ["username"]
        }
    },
    {
        "name": "get_repo_details",
        "description": "Fetch detailed metadata for a specific GitHub repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "The GitHub username (owner of the repo)."},
                "repo":     {"type": "string", "description": "The exact repository name."}
            },
            "required": ["username", "repo"]
        }
    }
]