# SmartAssign – Meeting Task Assignment System

This project processes audio recordings of team meetings and automatically:

- Converts meeting **audio** to text using Whisper (speech-to-text)  
- Identifies **tasks** mentioned in the meeting  
- Assigns each task to the most suitable **team member**  
- Extracts **deadline**, **priority**, and **dependencies** where possible  
- Outputs the result as a **JSON list** and a **table**



---

## 
Technologies Used

- Python 3  
- `openai-whisper` (for Speech-to-Text)  
- `spaCy` (`en_core_web_sm`) for NLP  
- `dateparser` + regex for deadlines  
- Pure Python logic for task classification & assignment  
- (Optional) Streamlit for a simple web UI  

---

## Project Structure

```text
meeting-task-assignment/
├─ data/
│  ├─ team_members.json        # Team members, roles, skills
│  ├─ sample-2.mp3             # Example meeting audio
│  ├─ last_transcript.txt      # Generated transcript
│  └─ tasks_output.json        # Generated task output (JSON)
├─ src/
│  ├─ __init__.py
│  ├─ stt_whisper.py           # Whisper-based speech-to-text
│  ├─ task_extractor.py        # Task extraction (NLP + rules)
│  ├─ assignment_logic.py      # Task-to-member assignment
│  └─ main.py                  # Main pipeline
├─ app.py                      # Streamlit web UI
├─ requirements.txt
└─ README.md

 Setup Instructions
1️. Create & activate virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux

2️. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

3️. Install FFmpeg (required for Whisper)
Install FFmpeg and add its bin folder to PATH
Then Verify the installation by :ffmpeg -version

------ How to Run (Command Line)-------
A – Use sample transcript (no audio needed)

In src/main.py, set:
USE_TEST_TEXT = True

Then run:
python -m src.main

This will Use the built-in sample meeting transcript (from the assignment PDF)
then
Extract and assign tasks and Save the results to data/tasks_output.json

 B – Use meeting audio (Whisper transcription)

Put your meeting audio inside data/, e.g.:
data/meeting_sample.mp3

In src/main.py, set:

USE_TEST_TEXT = False
audio_path = DATA_DIR / "meeting_sample.mp3"

Run:

python -m src.main



This will Transcribe the audio using Whisper and Extract tasks, deadlines, priorities, and dependencies

Saves the 
Transcript → data/last_transcript.txt
and
Tasks JSON → data/tasks_output.json

Optional: Streamlit Web UI

-------To launch the web UI:-------

streamlit run app.py

From the UI you can:

Use the sample transcript

Upload an audio file

See the transcript

View tasks in a table

Download tasks_output.json

----Logic Summary-----

Task Detection
Uses verbs and phrases such as: fix, design, write, update, we need to, should, let's, etc.

Deadlines
Extracted from phrases like tomorrow evening, by Friday, end of this week, next Monday, etc. using regex + dateparser.

Priority
Keyword-based:
critical, blocking → Critical
high priority, urgent → High
default → Medium

Dependencies
Phrases like depends on the login bug fix are attached as dependency for that task.

Assignment
If a person’s name is mentioned in the sentence, assign directly to them.
Otherwise, score each team member based on their role and skills and assign to the best match.



