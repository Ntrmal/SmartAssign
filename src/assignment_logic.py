# src/assignment_logic.py

from typing import List, Dict, Optional
import re


def normalize(text: str) -> str:
    return text.lower().strip()


def score_member_for_task(task_description: str, member: Dict) -> int:
    """
    Simple scoring based on keyword overlap between task description and member skills/role.
    """
    text = normalize(task_description)

    score = 0
    # Skill matches
    for skill in member.get("skills", []):
        if normalize(skill) in text:
            score += 3


    role = normalize(member.get("role", ""))
    if "frontend" in role and any(w in text for w in ["ui", "frontend", "screen", "login", "button", "react"]):
        score += 4
    if "backend" in role and any(w in text for w in ["database", "db", "api", "performance", "optimization", "backend"]):
        score += 4
    if "designer" in role or "ui/ux" in role:
        if any(w in text for w in ["design", "onboarding", "screen", "ui", "ux", "mockup", "layout"]):
            score += 4
    if "qa" in role or "tester" in role:
        if any(w in text for w in ["test", "testing", "unit tests", "automation", "quality"]):
            score += 4

    return score


def resolve_assignee(
    task_description: str,
    explicit_assignee_name: Optional[str],
    team_members: List[Dict]
) -> Optional[str]:
    """
    Decide which team member should be assigned to a task.
    1. If an explicit name is given & exists in team → use that.
    2. Otherwise, pick the member with highest score based on skills/role.
    """
    # 1) Explicit assignee
    if explicit_assignee_name:
        for member in team_members:
            if normalize(member["name"]) == normalize(explicit_assignee_name):
                return member["name"]

    # 2) Best match by scoring
    best_member = None
    best_score = -1

    for member in team_members:
        s = score_member_for_task(task_description, member)
        if s > best_score:
            best_score = s
            best_member = member

    return best_member["name"] if best_member else None
