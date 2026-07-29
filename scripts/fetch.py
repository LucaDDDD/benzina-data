#!/usr/bin/env python3
"""Scarica i CSV giornalieri MIMIT e li archivia gzippati per data di estrazione.

Idempotente: se il file per quella data di estrazione esiste già, non fa nulla.
Può quindi girare più volte al giorno senza produrre duplicati.
"""
from __future__ import annotations

import gzip
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://www.mimit.gov.it/images/exportCSV"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# Soglie prudenziali: molto sotto il normale (~93k prezzi, ~24k impianti)
# ma abbastanza alte da scartare pagine di errore o file troncati.
MIN_LINES = {"prezzo_alle_8": 50_000, "anagrafica_impianti_attivi": 15_000}


def fetch(name: str) -> str | None:
    """Scarica un CSV, lo valida e lo archivia. Ritorna la data di estrazione se nuovo."""
    req = urllib.request.Request(
        f"{BASE_URL}/{name}.csv",
        headers={"User-Agent": "benzina-data-collector/1.0 (github.com/LucaDDDD/benzina-data)"},
    )
    raw = urllib.request.urlopen(req, timeout=180).read()

    header = raw[:80].decode("utf-8", errors="replace")
    m = re.match(r"Estrazione del (\d{4}-\d{2}-\d{2})", header)
    if not m:
        sys.exit(f"{name}: intestazione inattesa: {header!r}")
    n_lines = raw.count(b"\n")
    if n_lines < MIN_LINES[name]:
        sys.exit(f"{name}: solo {n_lines} righe, file sospetto — non archivio")

    day = m.group(1)  # YYYY-MM-DD
    out = DATA_DIR / day[:4] / day[5:7] / f"{name}-{day.replace('-', '')}.csv.gz"
    if out.exists():
        print(f"{name}: estrazione {day} già archiviata, salto")
        return None

    out.parent.mkdir(parents=True, exist_ok=True)
    # mtime=0 rende il .gz deterministico: stesso contenuto -> stessi byte
    with open(out, "wb") as fh, gzip.GzipFile(fileobj=fh, mode="wb", mtime=0) as gz:
        gz.write(raw)
    print(f"{name}: archiviato {out.relative_to(DATA_DIR.parent)} ({n_lines} righe)")
    return day


def main() -> None:
    added = [d for d in (fetch(n) for n in MIN_LINES) if d]
    if not added:
        print("Nessun dato nuovo")
        return
    status = DATA_DIR / "last_update.json"
    status.write_text(
        json.dumps(
            {
                "ultima_estrazione": max(added),
                "aggiornato_il": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
