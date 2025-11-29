# src/stt_whisper.py

import whisper
from pathlib import Path


_model = whisper.load_model("small")


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe a meeting audio file using Whisper and return the text.
    :param audio_path: Path to audio file (.wav, .mp3, .m4a)
    :return: transcribed text
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"[STT] Transcribing: {audio_path}")
    result = _model.transcribe(str(audio_path))
    text = result.get("text", "").strip()
    print(f"[STT] Done. Length of transcript: {len(text)} characters")
    return text


if __name__ == "__main__":
    test_file = "../data/sample-2.mp3"
    transcript = transcribe_audio(test_file)
    print("TRANSCRIPT:\n", transcript)
