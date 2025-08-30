# VI→EN Reflex Trainer (Terminal)

A simple terminal app to drill **Vietnamese → English** reflexes.  
It shows a random Vietnamese sentence, **auto-generates audio** for VI (and EN on reveal), plays it, and lets you control the flow from the keyboard.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Data model

SQLite: `sentences.db` with table `sentences(id, vi, en, vi_audio, en_audio)`.

Seed data comes from `data/sentences.csv`. Add more lines as:  
`vi_text,en_text`  (commas inside text should be quoted).

## TTS engines

- **gTTS** (default): high quality (needs Internet). Saves MP3.
- **pyttsx3** (offline): saves WAV. You may need to pick a suitable **voice** on your OS.
  - Edit `config.json` to choose engine and voice IDs.
  - Run `python tools/list_voices.py` to list available voices.

## Controls (in app)

- [Enter]: I’ve said the EN sentence → show menu.
- `s`: Show English + play English audio.
- `r`: Repeat Vietnamese audio.
- `e`: Repeat English audio.
- `n`: Next random sentence.
- `q`: Quit.

Audio files are cached in `audio/` so each text is synthesized only once.
