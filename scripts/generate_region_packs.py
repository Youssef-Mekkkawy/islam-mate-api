"""
Islam Mate API — Offline Region Pack Generator
===============================================
Reads data/cities.db and outputs one compressed JSON file per country
into output/region_packs/<ISO2>.json.gz

Usage:
    python scripts/generate_region_packs.py              # generate all
    python scripts/generate_region_packs.py --upload     # generate + upload to HuggingFace
    python scripts/generate_region_packs.py --country EG # single country

HuggingFace dataset:
    elprofessorai/islam-mate-data
    Path inside dataset: region_packs/<ISO2>.json.gz

Requirements:
    pip install huggingface_hub tqdm   (only needed for --upload)
"""

import sqlite3
import json
import gzip
import shutil
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT  = Path(__file__).parent.parent
DB_PATH    = REPO_ROOT / "data" / "cities.db"
OUTPUT_DIR = REPO_ROOT / "output" / "region_packs"

HF_REPO    = "elprofessorai/islam-mate-data"
HF_SUBFOLDER = "region_packs"


# ── DB query ──────────────────────────────────────────────────────────────────

def load_all_cities(db_path: Path) -> dict[str, list[dict]]:
    """
    Read every city from cities.db.
    Returns dict keyed by ISO2 country code: { "EG": [...], "SA": [...], ... }
    """
    if not db_path.exists():
        print(f"[ERROR] DB not found: {db_path}")
        sys.exit(1)

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row

    rows = con.execute("""
        SELECT
            ci.name,
            ci.name_local,
            ci.latitude,
            ci.longitude,
            ci.timezone,
            g.name  AS governorate,
            c.name  AS country,
            c.iso2
        FROM cities ci
        JOIN governorates g ON g.id = ci.governorate_id
        JOIN countries    c ON c.id  = g.country_id
        ORDER BY c.iso2, ci.name
    """).fetchall()

    con.close()

    packs: dict[str, list[dict]] = {}
    for r in rows:
        iso2 = (r["iso2"] or "XX").upper()
        packs.setdefault(iso2, [])
        packs[iso2].append({
            "name":        r["name"],
            "name_local":  r["name_local"],
            "latitude":    r["latitude"],
            "longitude":   r["longitude"],
            "timezone":    r["timezone"],
            "governorate": r["governorate"],
            "country":     r["country"],
        })

    return packs


# ── Write pack ────────────────────────────────────────────────────────────────

def write_pack(iso2: str, cities: list[dict], out_dir: Path) -> Path:
    """Write one country pack as gzip-compressed JSON. Returns output path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{iso2}.json.gz"

    payload = {
        "schema_version": "1.0",
        "generated_at":   datetime.now(timezone.utc).isoformat(),
        "country_code":   iso2,
        "total_cities":   len(cities),
        "cities":         cities,
    }

    with gzip.open(out_path, "wt", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    return out_path


# ── Index file ────────────────────────────────────────────────────────────────

def write_index(packs: dict[str, list[dict]], out_dir: Path) -> Path:
    """Write index.json listing all available packs + city counts."""
    index = {
        "schema_version": "1.0",
        "generated_at":   datetime.now(timezone.utc).isoformat(),
        "total_countries": len(packs),
        "total_cities":    sum(len(v) for v in packs.values()),
        "base_url":        f"https://huggingface.co/datasets/{HF_REPO}/resolve/main/{HF_SUBFOLDER}",
        "packs": [
            {
                "country_code": iso2,
                "city_count":   len(cities),
                "file":         f"{iso2}.json.gz",
            }
            for iso2, cities in sorted(packs.items())
        ]
    }

    out_path = out_dir / "index.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return out_path


# ── HuggingFace upload ────────────────────────────────────────────────────────

def upload_to_hf(out_dir: Path, token: str | None = None):
    """Upload all files in out_dir to HuggingFace dataset."""
    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("[ERROR] huggingface_hub not installed. Run: pip install huggingface_hub")
        sys.exit(1)

    api = HfApi(token=token)

    files = list(out_dir.glob("*.json.gz")) + list(out_dir.glob("*.json"))
    if not files:
        print("[ERROR] No files to upload in", out_dir)
        sys.exit(1)

    print(f"\nUploading {len(files)} files to {HF_REPO}/{HF_SUBFOLDER} …")

    for file_path in sorted(files):
        dest = f"{HF_SUBFOLDER}/{file_path.name}"
        print(f"  ↑ {file_path.name} ({file_path.stat().st_size // 1024} KB) → {dest}")
        api.upload_file(
            path_or_fileobj=str(file_path),
            path_in_repo=dest,
            repo_id=HF_REPO,
            repo_type="dataset",
            commit_message=f"Update region pack: {file_path.name}",
        )

    print(f"\n✅ Upload complete. Access packs at:")
    print(f"   https://huggingface.co/datasets/{HF_REPO}/tree/main/{HF_SUBFOLDER}")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate offline region packs from cities.db"
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload generated packs to HuggingFace after generation"
    )
    parser.add_argument(
        "--country",
        metavar="ISO2",
        help="Generate only this country (e.g. --country EG)"
    )
    parser.add_argument(
        "--token",
        metavar="HF_TOKEN",
        help="HuggingFace write token (or set HF_TOKEN env var)"
    )
    parser.add_argument(
        "--output",
        metavar="DIR",
        default=str(OUTPUT_DIR),
        help=f"Output directory (default: {OUTPUT_DIR})"
    )
    args = parser.parse_args()

    out_dir = Path(args.output)

    # Load DB
    print(f"Reading {DB_PATH} …")
    all_packs = load_all_cities(DB_PATH)
    print(f"  {sum(len(v) for v in all_packs.values())} cities across {len(all_packs)} countries")

    # Filter if --country passed
    if args.country:
        iso2 = args.country.upper()
        if iso2 not in all_packs:
            print(f"[ERROR] Country '{iso2}' not found in DB. Available: {sorted(all_packs.keys())}")
            sys.exit(1)
        target_packs = {iso2: all_packs[iso2]}
    else:
        target_packs = all_packs

    # Generate packs
    print(f"\nGenerating {len(target_packs)} pack(s) → {out_dir}/")
    for iso2, cities in sorted(target_packs.items()):
        path = write_pack(iso2, cities, out_dir)
        kb = path.stat().st_size // 1024
        print(f"  ✓ {iso2}.json.gz  ({len(cities)} cities, {kb} KB)")

    # Write index (always, unless single-country mode)
    if not args.country:
        idx_path = write_index(all_packs, out_dir)
        print(f"\n  ✓ index.json written ({idx_path.stat().st_size // 1024} KB)")

    print(f"\nDone. {len(target_packs)} pack(s) in {out_dir}/")

    # Upload
    if args.upload:
        import os
        token = args.token or os.environ.get("HF_TOKEN")
        if not token:
            print("\n[ERROR] HuggingFace token required for upload.")
            print("  Option 1: --token hf_xxxxx")
            print("  Option 2: set HF_TOKEN environment variable")
            sys.exit(1)
        upload_to_hf(out_dir, token)


if __name__ == "__main__":
    main()