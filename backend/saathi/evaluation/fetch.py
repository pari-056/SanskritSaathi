"""Download the UD Sanskrit treebanks (CC BY-SA 4.0). They are not bundled with the app."""
from __future__ import annotations
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/UniversalDependencies"
CORPORA = {
    "sa_ufal-ud-test.conllu": f"{BASE}/UD_Sanskrit-UFAL/master/sa_ufal-ud-test.conllu",
    "sa_vedic-ud-test.conllu": f"{BASE}/UD_Sanskrit-Vedic/master/sa_vedic-ud-test.conllu",
}
DEFAULT_DIR = Path(__file__).resolve().parents[2] / "data" / "corpora"


def fetch_all(directory: Path = DEFAULT_DIR, force: bool = False) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    out = []
    for name, url in CORPORA.items():
        dest = directory / name
        if force or not dest.exists():
            with urllib.request.urlopen(url, timeout=60) as r:
                dest.write_bytes(r.read())
        out.append(dest)
    return out
