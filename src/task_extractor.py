# src/task_extractor.py

from typing import List, Dict, Optional
import re
import dateparser
import spacy

from src.assignment_logic import resolve_assignee


# Load spaCy English model once
_nlp = spacy.load("en_core_web_sm")

TASK_VERBS = [
    "fix", "resolve", "update", "write", "implement", "design", "create",
    "optimize", "improve", "refactor", "test", "review", "document"
]

PRIORITY_KEYWORDS = {
    "critical": "Critical",
    "blocker": "Critical",
    "high priority": "High",
    "urgent": "High",
    "medium": "Medium",
    "low": "Low",
}


def detect_priority(sentence: str) -> str:
    s = sentence.lower()
    # Exacting phrases
    for phrase, level in PRIORITY_KEYWORDS.items():
        if phrase in s:
            return level


    if "critical" in s or "blocking" in s:
        return "Critical"
    if "high" in s or "important" in s or "before release" in s:
        return "High"
    if "low priority" in s:
        return "Low"

    return "Medium"  # default


def detect_deadline(sentence: str) -> Optional[str]:
    """
    Uses dateparser to extract natural language dates like 'tomorrow evening', 'by Friday', etc.
    will return the phrase as text (not converted to specific date) to keep it simple.
    """
    # Look for common time expressions
    patterns = [
        r"\bby [A-Za-z]+\b",              # by Friday, by Monday
        r"\bby [A-Za-z]+ \d{1,2}\b",      # by March 3
        r"\btomorrow(?: morning| evening| night)?\b",
        r"\bnext [A-Za-z]+\b",            # next Monday, next week
        r"\bend of (this|the) week\b",
        r"\bbefore [A-Za-z]+'s release\b",
        r"\bthis week\b",
        r"\bthis sprint\b",
        r"\bnext sprint\b",
        r"\bby end of (this|the) month\b",
        r"\bby (EOD|end of day)\b",
        r"\bby tonight\b"
    ]

    for pat in patterns:
        m = re.search(pat, sentence, flags=re.IGNORECASE)
        if m:
            return m.group(0).strip()

    return None


def detect_dependencies(sentence: str) -> Optional[str]:
    s = sentence.lower()
    if "depends on" in s or "dependent on" in s or "after" in s:
        return sentence.strip()
    return None


def sentence_contains_task(sentence: str) -> bool:
    s = sentence.lower()


    if any(verb in s for verb in TASK_VERBS):
        return True

    # Common phrases implying a task
    pattern_phrases = [
        r"\bneed to\b",
        r"\bwe need\b",
        r"\bshould\b",
        r"\bmust\b",
        r"\bhave to\b",
        r"\bplan to\b",
        r"\blet's\b",
        r"\blets\b",
        r"\bsomeone has to\b",
        r"\bsomeone should\b",
        r"\bwe should\b",
    ]

    for pat in pattern_phrases:
        if re.search(pat, s):
            return True

    return False



def find_explicit_assignee(sentence: str, team_members: List[Dict]) -> Optional[str]:
    s = sentence.lower()
    for member in team_members:
        if member["name"].lower() in s:
            return member["name"]
    return None


def clean_description(sentence: str) -> str:
    """
    Clean up common prefixes like names, greetings, etc.
    """
    s = sentence.strip()

    # Remove leading phrases like "Sakshi, we need someone to"
    s = re.sub(r"^[A-Z][a-z]+,\s*", "", s)  # Name, ...
    s = re.sub(r"^(we|let's|lets)\s+(please\s+)?", "", s, flags=re.IGNORECASE)

    return s.strip()


def extract_tasks(transcript: str, team_members: List[Dict]) -> List[Dict]:
    doc = _nlp(transcript)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    tasks = []
    task_id = 1

    for sent in sentences:
        # Debug to see what spaCy is splitting
        print(f"[DEBUG] Sentence: {sent}")
        print(f"        Is task? {sentence_contains_task(sent)}")

        if not sentence_contains_task(sent):
            continue

        description = clean_description(sent)
        explicit_assignee = find_explicit_assignee(sent, team_members)
        deadline = detect_deadline(sent)
        priority = detect_priority(sent)
        dependency = detect_dependencies(sent)

        assignee = resolve_assignee(description, explicit_assignee, team_members)

        task = {
            "id": task_id,
            "description": description,
            "assigned_to": assignee,
            "explicit_assignee": explicit_assignee,
            "deadline": deadline,
            "priority": priority,
            "dependency": dependency,
            "source_sentence": sent,
        }
        tasks.append(task)
        task_id += 1

    return tasks
