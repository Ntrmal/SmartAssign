# src/main.py

from pathlib import Path
import json
from typing import List, Dict

from src.stt_whisper import transcribe_audio
from src.task_extractor import extract_tasks

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent  # root
DATA_DIR = BASE_DIR / "data"
TEAM_FILE = DATA_DIR / "team_members.json"
TRANSCRIPT_FILE = DATA_DIR / "last_transcript.txt"
TASKS_FILE = DATA_DIR / "tasks_output.json"


def load_team_members(path: Path = TEAM_FILE) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_transcript(text: str, path: Path = TRANSCRIPT_FILE):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"[MAIN] Transcript saved to {path.resolve()}")


def save_tasks(tasks: List[Dict], path: Path = TASKS_FILE):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)
    print(f"[MAIN] Tasks JSON saved to {path.resolve()}")


def pretty_print_tasks(tasks: List[Dict]):
    print("\n==== IDENTIFIED TASKS ====\n")
    if not tasks:
        print("No tasks detected.")
        return

    for t in tasks:
        print(f"Task #{t['id']}")
        print(f"  Description : {t['description']}")
        print(f"  Assigned To : {t['assigned_to']} (explicit: {t['explicit_assignee']})")
        print(f"  Deadline    : {t['deadline']}")
        print(f"  Priority    : {t['priority']}")
        print(f"  Dependency  : {t['dependency']}")
        print(f"  From        : {t['source_sentence']}")
        print("-" * 60)


def get_sample_transcript_from_pdf() -> str:
    return (
        "Hi everyone, let's discuss this week's priorities. "
        "Sakshi, we need someone to fix the critical login bug that users reported yesterday. "
        "This needs to be done by tomorrow evening since it's blocking users. "
        "Also, the database performance is really slow, Mohit you're good with backend optimization right? "
        "We should tackle this by end of this week, it's affecting the user experience. "
        "And we need to update the API documentation before Friday's release - this is high priority. "
        "Oh, and someone should design the new onboarding screens for the next sprint. "
        "Arjun, didn't you work on UI designs last month? This can wait until next Monday. "
        "One more thing - we need to write unit tests for the payment module. "
        "This depends on the login bug fix being completed first, so let's plan this for Wednesday."
    )


def main():
    USE_TEST_TEXT = False  # True = use sample text, False = use audio

    team_members = load_team_members()
    print("[MAIN] Loaded team members:", [m["name"] for m in team_members])

    if USE_TEST_TEXT:
        print("[MAIN] Using sample transcript from PDF (TEST MODE)")
        transcript = get_sample_transcript_from_pdf()
    else:
        audio_path = DATA_DIR / "sample-2.mp3"  # change name if needed
        print(f"[MAIN] Using Whisper on audio: {audio_path}")
        transcript = transcribe_audio(str(audio_path))

    save_transcript(transcript)

    tasks = extract_tasks(transcript, team_members)
    pretty_print_tasks(tasks)
    save_tasks(tasks)


if __name__ == "__main__":
    main()
