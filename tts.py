from pathlib import Path
from typing import Optional
import json, sys

PROJECT_DIR = Path(__file__).parent
CONFIG_PATH = PROJECT_DIR / "config.json"
AUDIO_DIR = PROJECT_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)

def synthesize(text: str, lang: str, basename: str, engine: Optional[str] = None) -> Path:
    """
    Create audio file for `text` in language `lang`.
    Returns the path to the generated audio file.
    Engine: 'gtts' (mp3) or 'pyttsx3' (wav). If None, use config.
    """
    cfg = load_config()
    engine = engine or cfg.get("tts_engine", "gtts")
    if engine == "gtts":
        return _synthesize_gtts(text, lang, basename, cfg)
    elif engine == "pyttsx3":
        return _synthesize_pyttsx3(text, lang, basename, cfg)
    else:
        raise ValueError(f"Unknown tts engine: {engine}")

def _synthesize_gtts(text: str, lang: str, basename: str, cfg) -> Path:
    from gtts import gTTS
    out_path = AUDIO_DIR / f"{basename}.mp3"
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(out_path.as_posix())
    return out_path

def _synthesize_pyttsx3(text: str, lang: str, basename: str, cfg) -> Path:
    import pyttsx3, time
    out_path = AUDIO_DIR / f"{basename}.wav"
    engine = pyttsx3.init()
    rate = cfg.get("pyttsx3", {}).get("rate", 175)
    volume = cfg.get("pyttsx3", {}).get("volume", 1.0)
    if lang == "vi":
        voice_id = cfg.get("pyttsx3", {}).get("vi_voice_id", "")
    else:
        voice_id = cfg.get("pyttsx3", {}).get("en_voice_id", "")
    if voice_id:
        engine.setProperty('voice', voice_id)
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)
    engine.save_to_file(text, out_path.as_posix())
    engine.runAndWait()
    # tiny wait for file system flush on some OSes
    time.sleep(0.1)
    return out_path

import subprocess
import platform
from pathlib import Path

def play_audio(path: Path):
    if not path.exists():
        return
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.Popen(["afplay", str(path)])
        elif system == "Linux":
            subprocess.Popen(["mpg123", str(path)])
        elif system == "Windows":
            import winsound
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            print(f"Don't know how to play audio on {system}")
    except Exception as e:
        print("Audio playback failed:", e)