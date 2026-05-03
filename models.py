"""Pydantic schemas for Madison Agent API."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    username: str = Field(..., description="GitHub username to analyze")


class Profile(BaseModel):
    login: Optional[str] = None
    name: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    public_repos: Optional[int] = None
    followers: Optional[int] = None
    following: Optional[int] = None
    created_at: Optional[str] = None


class RepoSummary(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    stars: Optional[int] = None
    forks: Optional[int] = None
    language: Optional[str] = None
    topics: Optional[list[Any]] = None
    updated_at: Optional[str] = None


class FeaturedRepo(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    description: Optional[str] = None
    stars: Optional[int] = None
    forks: Optional[int] = None
    open_issues: Optional[int] = None
    language: Optional[str] = None
    default_branch: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    homepage: Optional[str] = None


class AgentResult(BaseModel):
    username: Optional[str] = None
    profile: Optional[Profile] = None
    top_repos: Optional[list[RepoSummary]] = None
    featured_repo: Optional[FeaturedRepo] = None
    summary: Optional[str] = None


class AnalyzeResponse(BaseModel):
    success: bool
    data: AgentResult
