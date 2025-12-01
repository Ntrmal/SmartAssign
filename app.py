import json
from pathlib import Path
from typing import List, Dict

import pandas as pd
import streamlit as st

from src.stt_whisper import transcribe_audio
from src.task_extractor import extract_tasks


DATA_DIR = Path("data")
TEAM_MEMBERS_FILE = DATA_DIR / "team_members.json"


def load_team_members() -> List[Dict]:
    with open(TEAM_MEMBERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


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


def tasks_to_dataframe(tasks: List[Dict]) -> pd.DataFrame:
    # Converting internal task dict structure to a nice DataFrame
    rows = []
    for t in tasks:
        rows.append(
            {
                "ID": t.get("id"),
                "Task Description": t.get("description"),
                "Assigned To": t.get("assigned_to"),
                "Deadline": t.get("deadline"),
                "Priority": t.get("priority"),
                "Dependency": t.get("dependency"),
                "Reason/Source": t.get("source_sentence"),
            }
        )
    return pd.DataFrame(rows)


def main():
    st.set_page_config(
        page_title="Meeting Task Assignment",
        layout="wide",
    )

    st.title(" Meeting Task Assignment System")
    st.write(
        "Upload a meeting audio file or use the sample text, and this app will "
        "extract tasks, assign them to team members, and detect deadlines, priorities, and dependencies."
    )

    # Sidebar
    st.sidebar.header("Options")

    mode = st.sidebar.radio(
        "Input mode",
        ["Use sample text (from PDF)", "Upload audio file"],
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Team members")
    team_members = load_team_members()
    st.sidebar.json(team_members)

    transcript = None

    if mode == "Use sample text (from PDF)":
        st.info("Using the sample meeting transcript from the assignment PDF.")
        if st.button("Run on sample transcript"):
            transcript = get_sample_transcript_from_pdf()

    else:
        uploaded_file = st.file_uploader(
            "Upload meeting audio (.wav, .mp3, .m4a)", type=["wav", "mp3", "m4a"]
        )

        if uploaded_file is not None:
            st.audio(uploaded_file, format="audio/mp3")

            if st.button("Transcribe & extract tasks"):
                # Saving uploaded file temporarily in data/
                temp_path = DATA_DIR / uploaded_file.name
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                with st.spinner("Transcribing audio with Whisper..."):
                    transcript = transcribe_audio(str(temp_path))

    if transcript:
        st.subheader(" Transcript")
        with st.expander("Show transcript", expanded=False):
            st.write(transcript)

        with st.spinner("Extracting tasks from transcript..."):
            tasks = extract_tasks(transcript, team_members)

        if not tasks:
            st.warning("No tasks detected in the transcript.")
            return

        df = tasks_to_dataframe(tasks)

        st.subheader("Identified Tasks")
        st.dataframe(df, use_container_width=True)

        # Download JSON
        st.subheader(" Download Results")
        json_str = json.dumps(tasks, indent=4, ensure_ascii=False)
        st.download_button(
            label="Download tasks as JSON",
            data=json_str,
            file_name="tasks_output.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
