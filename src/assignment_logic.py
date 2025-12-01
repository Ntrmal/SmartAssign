# src/assignment_logic.py

from __future__ import annotations

from typing import List, Dict, Optional
import re


def tokenize(text: str) -> list[str]:
    """
    Simple tokenizer: letters only, lowercase, remove stopwords.
    Used to compute similarity between task text and member skills.
    """
    words = re.findall(r"[a-zA-Z]+", text.lower())
    stopwords = {
        "the", "a", "an", "to", "for", "and", "or", "is", "are", "of", "we", "this",
        "that", "it", "in", "on", "with", "by", "from", "at", "as", "be", "can",
        "our", "your", "their", "some", "any"
    }
    return [w for w in words if w not in stopwords]


def score_member_for_task(task_description: str, member: Dict) -> int:
    """
    Compute a score indicating how well this member fits the task,
    based on overlap between the task description and the member's
    role + skills + some role-specific boosts.
    """
    task_tokens = set(tokenize(task_description))

    role = member.get("role", "") or ""
    skills = member.get("skills", []) or []

    member_text_parts = [role] + skills
    member_tokens = set()
    for part in member_text_parts:
        member_tokens.update(tokenize(part))

    # Base score: token overlap
    overlap = task_tokens & member_tokens
    score = len(overlap) * 3  # each overlap worth 3 pts

    # Role-based boosts
    role_lower = role.lower()

    # Frontend-ish
    if "frontend" in role_lower or "front-end" in role_lower:
        if any(w in task_tokens for w in ["ui", "screen", "frontend", "react", "component", "layout"]):
            score += 2

    # Backend-ish
    if "backend" in role_lower or "back-end" in role_lower:
        if any(w in task_tokens for w in ["database", "db", "api", "apis", "performance", "latency", "server"]):
            score += 2

    # UI/UX / design
    if "designer" in role_lower or "ux" in role_lower or "ui " in role_lower:
        if any(w in task_tokens for w in ["design", "onboarding", "flow", "mockup", "screen", "figma"]):
            score += 2

    # QA / testing
    if "qa" in role_lower or "test" in role_lower:
        if any(w in task_tokens for w in ["test", "tests", "testing", "automation", "quality"]):
            score += 2

    return score


def resolve_assignee(
    description: str,
    explicit_assignee: Optional[str],
    team_members: List[Dict]
) -> str:
    """
    Decide who should be assigned this task.

    1. If explicit_assignee is given (name directly mentioned), use that.
    2. Otherwise, compute a score for each member based on their role & skills
       and pick the highest-scoring one.
    """
    if team_members is None or len(team_members) == 0:
        return explicit_assignee or "Unassigned"

    # If name already mentioned explicitly, trust that
    if explicit_assignee:
        return explicit_assignee

    # Otherwise, score all members
    best_score = -1
    best_member_name = team_members[0].get("name", "Unassigned")

    for member in team_members:
        name = member.get("name", "Unknown")
        member_score = score_member_for_task(description, member)
        if member_score > best_score:
            best_score = member_score
            best_member_name = name

    return best_member_name
