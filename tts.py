from pathlib import Path
from typing import Optional
import json
import subprocess
import platform
import time

PROJECT_DIR = Path(__file__).parent
CONFIG_PATH = PROJECT_DIR / "config.json"
AUDIO_DIR = PROJECT_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)


def load_config():
    if not CONFIG_PATH.exists():
        # Create a default config file if it doesn't exist
        default_config = {
            "tts_engine": "gtts",
            "pyttsx3": {
                "rate": 175,
                "volume": 1.0,
                "vi_voice_id": "",
                "en_voice_id": ""
            }
        }
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def synthesize(text: str, lang: str, basename: str, engine: Optional[str] = None) -> Path:
    cfg = load_config()
    engine = engine or cfg.get("tts_engine", "gtts")
    if engine == "gtts":
        return _synthesize_gtts(text, lang, basename)
    elif engine == "pyttsx3":
        return _synthesize_pyttsx3(text, lang, basename, cfg)
    else:
        raise ValueError(f"Unknown tts engine: {engine}")


def _synthesize_gtts(text: str, lang: str, basename: str) -> Path:
    from gtts import gTTS
    out_path = AUDIO_DIR / f"{basename}.mp3"
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(out_path.as_posix())
        return out_path
    except Exception as e:
        print(f"gTTS synthesis failed: {e}")
        return Path("")


def _synthesize_pyttsx3(text: str, lang: str, basename: str, cfg) -> Path:
    import pyttsx3
    out_path = AUDIO_DIR / f"{basename}.wav"
    try:
        engine = pyttsx3.init()
        rate = cfg.get("pyttsx3", {}).get("rate", 175)
        volume = cfg.get("pyttsx3", {}).get("volume", 1.0)

        voices = engine.getProperty('voices')
        for voice in voices:
            if lang in voice.languages:
                engine.setProperty('voice', voice.id)
                break

        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)
        engine.save_to_file(text, out_path.as_posix())
        engine.runAndWait()
        time.sleep(0.1)
        return out_path
    except Exception as e:
        print(f"pyttsx3 synthesis failed: {e}")
        return Path("")


def play_audio(path: Path):
    if not path.exists():
        print(f"Audio file not found: {path}")
        return

    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["afplay", str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif system == "Linux":
            subprocess.Popen(["mpg123", str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif system == "Windows":
            import winsound
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            print(f"Don't know how to play audio on {system}")
    except FileNotFoundError:
        print(f"Audio player not found. Please install a player for your OS (e.g., afplay on macOS, mpg123 on Linux).")
    except Exception as e:
        print("Audio playback failed:", e)