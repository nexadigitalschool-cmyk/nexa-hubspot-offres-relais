"""Tests du parsing VTT de scripts/yt-transcripts.py (aucun reseau requis)."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "yt-transcripts.py"
spec = importlib.util.spec_from_file_location("yt_transcripts", SCRIPT)
yt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yt)


# --- fixtures ---------------------------------------------------------------

# Sous-titres automatiques YouTube : fenetre glissante, chaque cue reprend la fin
# de la precedente, et le texte porte des balises de timing par mot.
AUTO_VTT = """WEBVTT
Kind: captions
Language: fr

00:00:00.120 --> 00:00:02.500 align:start position:0%
bonjour<00:00:00.500><c> a</c><00:00:00.900><c> tous</c>

00:00:02.500 --> 00:00:05.000 align:start position:0%
bonjour a tous
aujourd'hui<00:00:03.100><c> on</c><00:00:03.400><c> parle</c>

00:00:05.000 --> 00:00:08.000 align:start position:0%
aujourd'hui on parle
de transcription
"""

MANUAL_VTT = """WEBVTT

1
00:00:01.000 --> 00:00:03.000
Premiere phrase.

2
00:00:45.000 --> 00:00:47.000
Phrase bien plus tard.
"""


# --- parse_vtt --------------------------------------------------------------


def test_strips_inline_tags():
    lines = yt.parse_vtt(AUTO_VTT)
    assert all("<" not in text for _, text in lines)


def test_collapses_rolling_window_repeats():
    lines = yt.parse_vtt(AUTO_VTT)
    texts = [text for _, text in lines]
    assert texts == ["bonjour a tous", "aujourd'hui on parle", "de transcription"]


def test_keeps_cue_start_times():
    lines = yt.parse_vtt(AUTO_VTT)
    assert [round(t, 1) for t, _ in lines] == [0.1, 2.5, 5.0]


def test_ignores_headers_and_cue_indices():
    lines = yt.parse_vtt(MANUAL_VTT)
    texts = [text for _, text in lines]
    assert texts == ["Premiere phrase.", "Phrase bien plus tard."]
    assert not any(text.isdigit() for text in texts)


def test_empty_input_yields_nothing():
    assert yt.parse_vtt("WEBVTT\n\n") == []


def test_comma_decimal_separator_is_accepted():
    lines = yt.parse_vtt("WEBVTT\n\n00:00:02,250 --> 00:00:03,000\nsalut\n")
    assert lines == [(2.25, "salut")]


# --- temps ------------------------------------------------------------------


@pytest.mark.parametrize(
    "stamp,expected",
    [("00:00:00.000", 0.0), ("00:01:02.500", 62.5), ("01:00:00.000", 3600.0)],
)
def test_vtt_time_to_seconds(stamp, expected):
    assert yt.vtt_time_to_seconds(stamp) == expected


@pytest.mark.parametrize(
    "seconds,expected",
    [(0, "0:00"), (62, "1:02"), (600, "10:00"), (3723, "1:02:03")],
)
def test_format_timestamp(seconds, expected):
    assert yt.format_timestamp(seconds) == expected


# --- markdown ---------------------------------------------------------------


def test_markdown_groups_by_interval():
    lines = yt.parse_vtt(MANUAL_VTT)
    out = yt.to_markdown(lines, every=30)
    # 1s et 45s sont a plus de 30s d'ecart -> deux blocs horodates.
    assert out.count("**[") == 2
    assert "**[0:01]**" in out and "**[0:45]**" in out


def test_markdown_single_block_when_close_together():
    lines = yt.parse_vtt(AUTO_VTT)
    assert yt.to_markdown(lines, every=30).count("**[") == 1


def test_markdown_without_timestamps():
    out = yt.to_markdown(yt.parse_vtt(AUTO_VTT), every=0)
    assert "**[" not in out
    assert out.startswith("bonjour a tous")


def test_markdown_handles_empty():
    assert "Aucune transcription" in yt.to_markdown([])


# --- slug -------------------------------------------------------------------


def test_slug_is_filesystem_safe():
    slug = yt.safe_slug("Pourquoi 90% des SaaS échouent ?! (analyse)")
    assert "/" not in slug and " " not in slug and "?" not in slug
    assert slug.startswith("pourquoi-90")


def test_slug_is_truncated():
    assert len(yt.safe_slug("mot " * 100)) <= 60


def test_slug_never_empty():
    assert yt.safe_slug("///") == "video"


# --- sources ----------------------------------------------------------------


def test_resolve_sources_reads_file(tmp_path):
    listing = tmp_path / "urls.txt"
    listing.write_text("# commentaire\nhttps://youtu.be/A\n\nhttps://youtu.be/B\n")
    assert yt.resolve_sources([str(listing)]) == ["https://youtu.be/A", "https://youtu.be/B"]


def test_resolve_sources_passes_urls_through():
    urls = ["https://www.youtube.com/@chaine"]
    assert yt.resolve_sources(urls) == urls
