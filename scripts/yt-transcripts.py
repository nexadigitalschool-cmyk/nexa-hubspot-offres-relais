#!/usr/bin/env python3
"""Recupere en masse les transcriptions des videos les plus vues d'une chaine YouTube.

Etape 1 de la methode "chaine faceless" : plutot que de passer une video a la fois
dans un outil web, on aspire d'un coup le top N d'une chaine pour avoir de quoi
analyser un pattern plutot qu'un cas isole.

Ne depend que de `yt-dlp` (les sous-titres sont recuperes en VTT natif, donc
ffmpeg n'est PAS necessaire ici, contrairement a la skill /watch).

    pipx install yt-dlp        # ou: brew install yt-dlp

    # Top 10 des videos les plus vues d'une chaine
    python3 scripts/yt-transcripts.py "https://www.youtube.com/@chaine" --top 10

    # Une playlist entiere, sans limite de vues
    python3 scripts/yt-transcripts.py "https://youtube.com/playlist?list=XXX" --top 0

    # Des URLs precises (ou un fichier texte, une URL par ligne)
    python3 scripts/yt-transcripts.py "https://youtu.be/A" "https://youtu.be/B"
    python3 scripts/yt-transcripts.py urls.txt

Sortie : un fichier .md par video dans `transcripts/`, plus `index.md` et
`index.json` pour la vue d'ensemble.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TAG_RE = re.compile(r"<[^>]+>")
CUE_RE = re.compile(
    r"^(\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[.,]\d{3})"
)
UNSAFE_RE = re.compile(r"[^\w\-]+", re.UNICODE)


# --------------------------------------------------------------------------- VTT


def vtt_time_to_seconds(stamp: str) -> float:
    """'00:01:02.500' -> 62.5"""
    hours, minutes, rest = stamp.split(":")
    seconds = rest.replace(",", ".")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def parse_vtt(raw: str) -> list[tuple[float, str]]:
    """VTT -> [(seconde, ligne)], balises retirees et repetitions supprimees.

    Les sous-titres automatiques YouTube arrivent en fenetre glissante : chaque cue
    reprend la fin de la precedente. On ne garde donc une ligne que si elle differe
    de la derniere ligne deja retenue.
    """
    lines: list[tuple[float, str]] = []
    current_start: float | None = None
    last_kept: str | None = None

    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("WEBVTT", "NOTE", "STYLE", "Kind:", "Language:")):
            continue

        match = CUE_RE.match(line)
        if match:
            current_start = vtt_time_to_seconds(match.group(1))
            continue

        if current_start is None:
            continue

        text = TAG_RE.sub("", line).strip()
        # Une ligne composee uniquement d'un index de cue n'est pas du texte.
        if not text or text.isdigit():
            continue
        if text == last_kept:
            continue

        lines.append((current_start, text))
        last_kept = text

    return lines


def to_markdown(lines: list[tuple[float, str]], every: int = 30) -> str:
    """Regroupe en paragraphes, avec un timecode toutes les `every` secondes."""
    if not lines:
        return "_Aucune transcription disponible._"
    if every <= 0:
        return " ".join(text for _, text in lines)

    blocks: list[str] = []
    buffer: list[str] = []
    block_start = lines[0][0]

    for seconds, text in lines:
        if buffer and seconds - block_start >= every:
            blocks.append(f"**[{format_timestamp(block_start)}]** " + " ".join(buffer))
            buffer = []
            block_start = seconds
        buffer.append(text)

    if buffer:
        blocks.append(f"**[{format_timestamp(block_start)}]** " + " ".join(buffer))
    return "\n\n".join(blocks)


# ------------------------------------------------------------------------ yt-dlp


def run_ytdlp(args: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["yt-dlp", *args], capture_output=True, text=True, timeout=timeout
    )


def expand_source(source: str, limit: int) -> list[dict]:
    """Chaine / playlist / video -> liste d'entrees {id, title, url, view_count, ...}."""
    args = ["--flat-playlist", "--dump-single-json", "--ignore-errors"]
    if limit > 0:
        args += ["--playlist-end", str(limit)]
    args.append(source)

    result = run_ytdlp(args)
    if result.returncode != 0 and not result.stdout.strip():
        print(f"  ! yt-dlp a echoue sur {source}", file=sys.stderr)
        for err_line in result.stderr.strip().splitlines()[-3:]:
            print(f"    {err_line}", file=sys.stderr)
        return []

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  ! reponse yt-dlp illisible pour {source}", file=sys.stderr)
        return []

    entries = payload.get("entries")
    if entries is None:  # video unique
        entries = [payload]

    videos: list[dict] = []
    for entry in entries:
        if not entry:
            continue
        # Une chaine expose des onglets ("Videos", "Shorts", "Live") comme sous-playlists.
        if entry.get("_type") == "playlist" and entry.get("entries"):
            videos.extend(e for e in entry["entries"] if e)
            continue
        if entry.get("id"):
            videos.append(entry)
    return videos


def fetch_transcript(video_id: str, langs: str, workdir: Path) -> tuple[str, str] | None:
    """Telecharge les sous-titres d'une video. -> (langue, contenu VTT) ou None."""
    result = run_ytdlp(
        [
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs",
            langs,
            "--sub-format",
            "vtt",
            "--ignore-errors",
            "-o",
            str(workdir / "%(id)s.%(ext)s"),
            f"https://www.youtube.com/watch?v={video_id}",
        ]
    )

    files = sorted(workdir.glob(f"{video_id}*.vtt"))
    if not files:
        if result.returncode != 0:
            tail = result.stderr.strip().splitlines()[-1:] or [""]
            print(f"    (yt-dlp: {tail[0][:120]})", file=sys.stderr)
        return None

    # Prefere un sous-titre manuel (nom court) a un auto-genere (suffixe .orig / -auto).
    chosen = min(files, key=lambda p: len(p.name))
    lang = chosen.stem.replace(video_id, "").strip(".") or "?"
    return lang, chosen.read_text(encoding="utf-8", errors="replace")


# ------------------------------------------------------------------------ sortie


def safe_slug(text: str, maxlen: int = 60) -> str:
    slug = UNSAFE_RE.sub("-", text.strip().lower()).strip("-")
    return (slug[:maxlen].rstrip("-") or "video")


def write_video_file(out_dir: Path, rank: int, video: dict, lang: str, body: str) -> Path:
    title = video.get("title") or video.get("id", "sans-titre")
    path = out_dir / f"{rank:02d}-{safe_slug(title)}.md"

    views = video.get("view_count")
    duration = video.get("duration")
    header = [
        f"# {title}",
        "",
        f"- URL : https://www.youtube.com/watch?v={video['id']}",
        f"- Vues : {views:,}".replace(",", " ") if isinstance(views, int) else "- Vues : inconnu",
        f"- Duree : {format_timestamp(duration)}" if isinstance(duration, (int, float)) else "- Duree : inconnue",
        f"- Sous-titres : {lang}",
        "",
        "---",
        "",
    ]
    path.write_text("\n".join(header) + body + "\n", encoding="utf-8")
    return path


def write_index(out_dir: Path, collected: list[dict]) -> None:
    (out_dir / "index.json").write_text(
        json.dumps(collected, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    rows = ["# Transcriptions collectees", "", "| # | Titre | Vues | Duree | Fichier |", "|---|---|---|---|---|"]
    for item in collected:
        views = item.get("view_count")
        views_str = f"{views:,}".replace(",", " ") if isinstance(views, int) else "?"
        duration = item.get("duration")
        dur_str = format_timestamp(duration) if isinstance(duration, (int, float)) else "?"
        title = (item.get("title") or "").replace("|", "\\|")
        rows.append(
            f"| {item['rank']} | {title} | {views_str} | {dur_str} | `{item['file']}` |"
        )
    (out_dir / "index.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


# -------------------------------------------------------------------------- main


def resolve_sources(raw_sources: list[str]) -> list[str]:
    """Remplace un chemin de fichier par les URLs qu'il contient."""
    sources: list[str] = []
    for item in raw_sources:
        path = Path(item)
        if path.is_file():
            sources.extend(
                line.strip()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.strip().startswith("#")
            )
        else:
            sources.append(item)
    return sources


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aspire les transcriptions des videos les plus vues d'une chaine YouTube.",
    )
    parser.add_argument("sources", nargs="+", help="URL de chaine, playlist, video, ou fichier d'URLs")
    parser.add_argument("--top", type=int, default=10, help="garder les N plus vues (0 = toutes). Defaut: 10")
    parser.add_argument("--limit", type=int, default=100, help="nombre de videos scannees par source. Defaut: 100")
    parser.add_argument("--lang", default="fr,en", help="langues de sous-titres, par preference. Defaut: fr,en")
    parser.add_argument("--out", type=Path, default=Path("transcripts"), help="dossier de sortie. Defaut: transcripts/")
    parser.add_argument("--every", type=int, default=30, help="un timecode toutes les N secondes (0 = aucun). Defaut: 30")
    args = parser.parse_args()

    if not shutil.which("yt-dlp"):
        sys.exit("yt-dlp introuvable.\n  pipx install yt-dlp   (ou: brew install yt-dlp)")

    sources = resolve_sources(args.sources)
    print(f"Sources : {len(sources)}", file=sys.stderr)

    videos: list[dict] = []
    seen: set[str] = set()
    for source in sources:
        print(f"  scan {source}", file=sys.stderr)
        for video in expand_source(source, args.limit):
            if video["id"] not in seen:
                seen.add(video["id"])
                videos.append(video)

    if not videos:
        sys.exit("Aucune video trouvee. Verifie l'URL et l'acces reseau.")

    # Les entrees sans compteur de vues passent en dernier plutot que d'etre jetees.
    videos.sort(key=lambda v: v.get("view_count") or -1, reverse=True)
    if args.top > 0:
        videos = videos[: args.top]

    missing_views = sum(1 for v in videos if not isinstance(v.get("view_count"), int))
    if missing_views:
        print(
            f"  ! {missing_views}/{len(videos)} videos sans compteur de vues : "
            "le classement par popularite est partiel.",
            file=sys.stderr,
        )

    args.out.mkdir(parents=True, exist_ok=True)
    collected: list[dict] = []
    failed: list[str] = []

    with tempfile.TemporaryDirectory(prefix="yt-subs-") as tmp:
        workdir = Path(tmp)
        for rank, video in enumerate(videos, start=1):
            title = video.get("title") or video["id"]
            print(f"  [{rank}/{len(videos)}] {title[:70]}", file=sys.stderr)

            fetched = fetch_transcript(video["id"], args.lang, workdir)
            if not fetched:
                print("    -> pas de sous-titres, ignoree", file=sys.stderr)
                failed.append(title)
                continue

            lang, vtt = fetched
            lines = parse_vtt(vtt)
            if not lines:
                print("    -> sous-titres vides, ignoree", file=sys.stderr)
                failed.append(title)
                continue

            path = write_video_file(args.out, rank, video, lang, to_markdown(lines, args.every))
            collected.append(
                {
                    "rank": rank,
                    "id": video["id"],
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={video['id']}",
                    "view_count": video.get("view_count"),
                    "duration": video.get("duration"),
                    "lang": lang,
                    "words": sum(len(text.split()) for _, text in lines),
                    "file": path.name,
                }
            )

    if not collected:
        sys.exit("Aucune transcription recuperee (aucune video ne portait de sous-titres).")

    write_index(args.out, collected)

    total_words = sum(item["words"] for item in collected)
    print(
        f"\n{len(collected)} transcriptions -> {args.out}/ ({total_words:,} mots)".replace(",", " "),
        file=sys.stderr,
    )
    if failed:
        print(f"{len(failed)} sans sous-titres : {', '.join(t[:40] for t in failed[:5])}", file=sys.stderr)
    print(f"Vue d'ensemble : {args.out}/index.md", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
