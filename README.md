# movie-transcriber

This project automates movie transcription and subtitle creation using OpenAI's Whisper Transcriber. It's specifically designed for efficiently handling foreign media, initially targeting Japanese.

**Motivation**

Inspired by Whisper's capabilities, I wanted to streamline transcribing movies stored in a PikPak media drive. Manually transcribing each movie was time-consuming, prompting the creation of this automated solution.

**How it Works**

1. **Daemon Setup:**
   - Run `pip install -r requirements.txt` to install dependencies.
   - Start the background process using `python whisper_daemon_simple.py`.
   - Consider using `tmux` for session management (optional).

2. **Automated Transcription and Translation:**
   - The script continuously monitors a designated directory (configurable on line 9 of `whisper_daemon_simple.py`).
   - When a new `.mp4` file is detected, Whisper is invoked to transcribe and translate the video content.
   - Upon completion, the script automatically moves both the original media file and the generated subtitle file (`.srt`) to a separate location (configurable on line 9 of `pikpak_file_translator.py`).

**License**

This project is distributed under the MIT License.