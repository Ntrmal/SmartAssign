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

