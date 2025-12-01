# src/task_extractor.py

from __future__ import annotations

from typing import List, Dict, Optional
import re

import dateparser
import spacy

from src.assignment_logic import resolve_assignee

# Load spaCy model once
_nlp = spacy.load("en_core_web_sm")

# Common verbs that indicate tasks / actions
TASK_VERBS = {
    "fix", "resolve", "update", "write", "implement", "design", "create",
    "optimize", "improve", "refactor", "test", "review", "document",
    "build", "deploy", "analyze", "investigate", "prepare", "setup",
    "set up", "configure", "check"
}

PRIORITY_KEYWORDS = {
    "critical": "Critical",
    "blocking": "Critical",
    "blocker": "Critical",
    "high priority": "High",
    "urgent": "High",
    "low priority": "Low",
}


def sentence_contains_task(sentence: str) -> bool:
    """
    does this sentence look like it contains a task?
    """
    s = sentence.lower()

    # Filter out obvious meta / greeting sentences
    if "let's discuss" in s and "priorities" in s:
        return False

    # Explicit task verbs
    for verb in TASK_VERBS:
        if verb in s:
            return True

    # Common phrases indicating action / tasks
    patterns = [
        r"\bwe need to\b",
        r"\bneed to\b",
        r"\bwe should\b",
        r"\bshould\b",
        r"\bmust\b",
        r"\bhave to\b",
        r"\bplan to\b",
        r"\blet's\b",
        r"\blets\b",
        r"\bsomeone should\b",
        r"\bsomeone has to\b",
    ]
    for pat in patterns:
        if re.search(pat, s):
            return True

    return False


def detect_deadline(sentence: str) -> Optional[str]:
    """
    Extract deadline phrase from a sentence.
    Returns the textual part describing time, not a parsed date.
    """
    s = sentence.lower()

    #  patterns
    deadline_patterns = [
        r"by (tomorrow(?: morning| evening)?)",
        r"by ([a-z]+day)",
        r"before ([^.,;]+)",
        r"(tomorrow(?: morning| evening)?)",
        r"(end of this week|by end of this week)",
        r"(next [a-z]+day)",
        r"(next sprint)",
        r"(this week)",
        r"(by [0-9]{1,2}(st|nd|rd|th)?)"
    ]

    for pat in deadline_patterns:
        m = re.search(pat, s)
        if m:
            return m.group(0).strip()


    try:
        parsed = dateparser.parse(sentence)
        if parsed:

            return sentence.strip()
    except Exception:
        pass

    return None
def detect_priority(sentence: str) -> str:
    """
    Determining priority from the sentence based on keywords.
    """
    s = sentence.lower()

    for key, level in PRIORITY_KEYWORDS.items():
        if key in s:
            return level

    # If nothing special, medium by default
    return "Medium"

def detect_dependencies(sentence: str) -> Optional[str]:
    """
    Detect if this sentence expresses a dependency.
    """
    s = sentence.lower()
    if "depends on" in s or "dependent on" in s:
        return sentence.strip()
    return None


def clean_description(sentence: str) -> str:
    """

    - remove leading names & filler like 'oh,', 'one more thing -', etc.
    """
    s = sentence.strip()

    # Remove leading "Oh" .
    s = re.sub(r"^(oh|so|and|also)[, -]+", "", s, flags=re.IGNORECASE)

    # Remove leading "One more thing"
    s = re.sub(r"^one more thing[,\s-]+", "", s, flags=re.IGNORECASE)

    # Remove leading name ("Sakshi," "Mohit," etc.)
    s = re.sub(r"^[A-Z][a-z]+[,:\-]\s*", "", s)


    if s and s[0].isupper():

        if len(s) > 1 and s[:2].isalpha():
            s = s[0].lower() + s[1:]

    return s.strip()


def find_explicit_assignee(sentence: str, team_members: List[Dict]) -> Optional[str]:
    """
    If a team member's name is explicitly mentioned in the sentence,
    return that name. Otherwise None.
    """
    s = sentence.lower()
    for member in team_members:
        name = member.get("name", "")
        if not name:
            continue
        if name.lower() in s:
            return name
    return None


def classify_sentence(sentence: str) -> str:
    """
    Classify a sentence into:
    - 'task'        : main action item
    - 'deadline'    : contains only time/deadline info
    - 'priority'    : contains only priority info
    - 'dependency'  : contains dependency info
    - 'other'       : not relevant
    """
    s = sentence.lower().strip()

    # greeting
    if not s:
        return "other"
    if "let's discuss" in s and "priorities" in s:
        return "other"

    # Task?
    if sentence_contains_task(sentence):
        return "task"

    # Dependency?
    if "depends on" in s or "dependent on" in s:
        return "dependency"

    # Deadline only?
    if detect_deadline(sentence):
        return "deadline"

    # Priority only?
    if any(key in s for key in PRIORITY_KEYWORDS.keys()):
        return "priority"

    return "other"

def build_reason(
    description: str,
    assigned_to: str,
    explicit_assignee: Optional[str],
    team_members: List[Dict]
) -> str:

    if explicit_assignee:
        return f"Assigned to {assigned_to} because they were mentioned explicitly in the meeting."

    member = next((m for m in team_members if m.get("name") == assigned_to), None)
    if not member:
        return f"Assigned to {assigned_to} based on best role/skill match."

    role = (member.get("role") or "").lower()

    if "frontend" in role:
        return f"Assigned to {assigned_to} due to frontend/UI expertise."
    if "backend" in role:
        return f"Assigned to {assigned_to} due to backend, database and API expertise."
    if "designer" in role or "ux" in role or "ui " in role:
        return f"Assigned to {assigned_to} due to UI/UX design experience."
    if "qa" in role or "test" in role:
        return f"Assigned to {assigned_to} due to QA/testing responsibilities."

    return f"Assigned to {assigned_to} based on role and skills similarity."

def extract_tasks(transcript: str, team_members: List[Dict]) -> List[Dict]:

    doc = _nlp(transcript)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    tasks: List[Dict] = []
    task_id = 1
    last_task: Optional[Dict] = None

    for sent in sentences:
        kind = classify_sentence(sent)



        if kind == "task":
            description = clean_description(sent)
            explicit_assignee = find_explicit_assignee(sent, team_members)
            deadline = detect_deadline(sent)
            priority = detect_priority(sent)
            dependency = detect_dependencies(sent)

            assignee = resolve_assignee(description, explicit_assignee, team_members)
            reason = build_reason(description, assignee, explicit_assignee, team_members)

            task = {
                "id": task_id,
                "description": description,
                "assigned_to": assignee,
                "explicit_assignee": explicit_assignee,
                "deadline": deadline,
                "priority": priority,
                "dependency": dependency,
                "reason": reason,
                "source_sentence": sent,
            }

            tasks.append(task)
            last_task = task
            task_id += 1

        elif last_task:

            if kind == "deadline":

                if not last_task.get("deadline"):
                    last_task["deadline"] = detect_deadline(sent)

            elif kind == "priority":

                last_task["priority"] = detect_priority(sent)

            elif kind == "dependency":
                last_task["dependency"] = detect_dependencies(sent) or sent.strip()



    return tasks
