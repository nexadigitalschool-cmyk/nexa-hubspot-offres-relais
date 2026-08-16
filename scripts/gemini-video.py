#!/usr/bin/env python3
"""Lecture native d'une video YouTube par l'API Gemini (image + son, en une requete).

Complement de la skill /watch :
  - /watch  -> telecharge, extrait des frames, transcrit, et rend la main a Claude.
              Fonctionne sur YouTube, TikTok, Vimeo, X, fichiers locaux.
  - ce script -> envoie l'URL YouTube telle quelle a Gemini, qui lit la video
              nativement (visuel + audio) jusqu'a plusieurs heures en un appel.
              YouTube uniquement.

Pure stdlib, aucune dependance.

    export GEMINI_API_KEY=...            # https://aistudio.google.com/apikey
    python3 scripts/gemini-video.py --list-models
    python3 scripts/gemini-video.py "https://youtu.be/XXXX" "Resume les 3 idees cles"
    python3 scripts/gemini-video.py "$URL" "Que montre-t-il ?" --start 2:15 --end 2:45
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_ROOT = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
TIMEOUT = 600


def load_env() -> None:
    """Charge GEMINI_API_KEY depuis .env (repo) puis ~/.config/watch/.env.

    Les variables deja presentes dans l'environnement gagnent toujours.
    """
    for candidate in (Path.cwd() / ".env", Path.home() / ".config" / "watch" / ".env"):
        if not candidate.is_file():
            continue
        for raw in candidate.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value


def parse_timecode(value: str) -> str:
    """'90' | '1:30' | '01:02:03' -> '90s' (format startOffset/endOffset de Gemini)."""
    parts = value.strip().split(":")
    if not all(p.isdigit() for p in parts) or len(parts) > 3:
        raise argparse.ArgumentTypeError(f"timecode invalide: {value!r} (SS, MM:SS ou HH:MM:SS)")
    seconds = 0
    for part in parts:
        seconds = seconds * 60 + int(part)
    return f"{seconds}s"


def call_api(path: str, api_key: str, payload: dict | None = None) -> dict:
    url = f"{API_ROOT}/{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    request.add_header("x-goog-api-key", api_key)
    if data:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            message = json.loads(body)["error"]["message"]
        except (ValueError, KeyError, TypeError):
            message = body[:500]
        sys.exit(f"Erreur API Gemini {exc.code}: {message}")
    except urllib.error.URLError as exc:
        sys.exit(f"Impossible de joindre {API_ROOT}: {exc.reason}")


def list_models(api_key: str) -> int:
    payload = call_api("models", api_key)
    for model in payload.get("models", []):
        if "generateContent" not in model.get("supportedGenerationMethods", []):
            continue
        name = model.get("name", "").removeprefix("models/")
        print(f"{name:<40} {model.get('displayName', '')}")
    return 0


def watch(args: argparse.Namespace, api_key: str) -> int:
    file_data: dict = {"file_uri": args.url}
    video_metadata: dict = {}
    if args.start:
        video_metadata["start_offset"] = args.start
    if args.end:
        video_metadata["end_offset"] = args.end
    if args.fps is not None:
        video_metadata["fps"] = args.fps

    part: dict = {"file_data": file_data}
    if video_metadata:
        part["video_metadata"] = video_metadata

    payload = {
        "contents": [{"parts": [part, {"text": args.prompt}]}],
    }

    response = call_api(f"models/{args.model}:generateContent", api_key, payload)

    candidates = response.get("candidates") or []
    if not candidates:
        feedback = response.get("promptFeedback", {})
        sys.exit(f"Aucune reponse. promptFeedback={json.dumps(feedback, ensure_ascii=False)}")

    for chunk in candidates[0].get("content", {}).get("parts", []):
        if "text" in chunk:
            print(chunk["text"])

    usage = response.get("usageMetadata", {})
    if usage:
        print(
            f"\n---\nTokens: {usage.get('promptTokenCount', '?')} entree"
            f" / {usage.get('candidatesTokenCount', '?')} sortie"
            f" (modele {args.model})",
            file=sys.stderr,
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Lit une video YouTube nativement via l'API Gemini (visuel + audio).",
    )
    parser.add_argument("url", nargs="?", help="URL YouTube publique")
    parser.add_argument(
        "prompt",
        nargs="?",
        default="Resume cette video : structure, moments cles, ce qui est dit et montre.",
        help="Question posee sur la video",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"defaut: {DEFAULT_MODEL}")
    parser.add_argument("--start", type=parse_timecode, help="debut du extrait (SS, MM:SS, HH:MM:SS)")
    parser.add_argument("--end", type=parse_timecode, help="fin de l'extrait (SS, MM:SS, HH:MM:SS)")
    parser.add_argument("--fps", type=float, help="images par seconde echantillonnees (defaut API: 1)")
    parser.add_argument("--list-models", action="store_true", help="liste les modeles disponibles")
    args = parser.parse_args()

    load_env()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit(
            "GEMINI_API_KEY absent.\n"
            "  1. Cree une cle gratuite sur https://aistudio.google.com/apikey\n"
            "  2. export GEMINI_API_KEY=...  (ou ajoute-la dans .env / ~/.config/watch/.env)"
        )

    if args.list_models:
        return list_models(api_key)

    if not args.url:
        parser.error("url manquante (ou utilise --list-models)")

    return watch(args, api_key)


if __name__ == "__main__":
    sys.exit(main())
