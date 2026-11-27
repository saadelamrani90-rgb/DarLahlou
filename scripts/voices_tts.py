"""Génère les pistes témoin (edge-tts) + les visèmes Rhubarb pour une scène.
Usage : python scripts/voices_tts.py storyboard/scene_A_dialogue.json [dossier_audio]
Sorties : audio/scene_A/<id>.wav et <id>.json (repères de bouche A..H, X)."""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICES = {  # réglages témoin : à remplacer par les vocaux de Saad
    "brahim": ("ar-MA-JamalNeural", "-5%", "-6Hz"),
    "lhssen": ("ar-MA-JamalNeural", "-12%", "+8Hz"),
    "fatema": ("ar-MA-MounaNeural", "+0%", "+0Hz"),
}
RHUBARB = os.path.join(ROOT, "tools", "Rhubarb-Lip-Sync-1.14.0-Linux", "rhubarb")
src = json.load(open(sys.argv[1]))
out = os.path.join(ROOT, "audio", sys.argv[2] if len(sys.argv) > 2 else "scene_A")
os.makedirs(out, exist_ok=True)
env = dict(os.environ, SSL_CERT_FILE="/root/.ccr/ca-bundle.crt")
for r in src["repliques"]:
    v, rate, pitch = VOICES[r["perso"]]
    mp3, wav, cues = (os.path.join(out, r["id"] + e) for e in (".mp3", ".wav", ".json"))
    if not os.path.exists(wav):
        subprocess.run(["edge-tts", "--proxy", os.environ.get("HTTPS_PROXY", ""), "--voice", v, f"--rate={rate}",
                        f"--pitch={pitch}", "--text", r["arabe"], "--write-media", mp3], check=True, env=env)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", "44100", "-ac", "1", wav], check=True)
        os.remove(mp3)
    subprocess.run([RHUBARB, "-q", "-r", "phonetic", "-f", "json", "-o", cues, wav], check=True)
    d = json.load(open(cues))
    print(r["id"], r["perso"], round(d["metadata"]["duration"], 2), "s,", len(d["mouthCues"]), "repères")
