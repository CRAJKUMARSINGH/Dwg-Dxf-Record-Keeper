"""
ETERNAL_RESEARCH_CHILD — Autonomous Research Daemon
====================================================
Scans DXF/DWG source folders every 15 minutes, studies drawings,
compares against layer standards, and proposes structured refinements.

Usage:
    python research_daemon.py            # continuous loop
    python research_daemon.py --once     # single cycle and exit
    python research_daemon.py --dry-run  # show proposals, no prompts
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path

import yaml

# ── Optional ezdxf ────────────────────────────────────────────────────────────
try:
    import ezdxf
    from ezdxf import readfile as dxf_readfile
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False
    warnings.warn(
        "ezdxf not installed — falling back to file-metadata-only analysis. "
        "Install with: pip install ezdxf",
        stacklevel=1,
    )

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DAEMON_DIR = ROOT / "ETERNAL_RESEARCH_CHILD"
PROPOSALS_DIR = DAEMON_DIR / "proposals"
ACCEPTED_FILE = DAEMON_DIR / "accepted_proposals.jsonl"
REJECTED_FILE = DAEMON_DIR / "rejected_proposals.jsonl"
RESEARCH_LOG  = DAEMON_DIR / "RESEARCH_LOG.md"
LAYER_STANDARDS_FILE = ROOT / "config" / "layer_standards.yaml"

SOURCE_FOLDERS: list[Path] = [
    ROOT / "DRAWINGS_FROM_RAJKUMAR_DESIGNS",
    ROOT / "COMPONENT_DRAWINGS_SORTED",
    ROOT / "COLLECTION FROM RECORD",
]

SCAN_INTERVAL_SECONDS = 15 * 60   # 15 minutes
MAX_FILES_TO_STUDY    = 3

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("research_daemon")

# ── Standards loader ──────────────────────────────────────────────────────────

def load_layer_standards() -> dict:
    if not LAYER_STANDARDS_FILE.exists():
        log.warning("layer_standards.yaml not found at %s", LAYER_STANDARDS_FILE)
        return {}
    with LAYER_STANDARDS_FILE.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}

# ── DXF analysis ─────────────────────────────────────────────────────────────

def _metadata_only(path: Path) -> dict:
    return {
        "layers": [], "blocks": [], "text_heights": [],
        "dim_styles": [], "entity_counts": {},
        "has_title_block": False, "source": "metadata_only",
    }


def analyze_dxf(path: Path) -> dict:
    if not EZDXF_AVAILABLE:
        log.warning("ezdxf unavailable — using metadata only for %s", path.name)
        return _metadata_only(path)
    try:
        doc = dxf_readfile(str(path))
        msp = doc.modelspace()
        layers     = [layer.dxf.name for layer in doc.layers]
        blocks     = [b.name for b in doc.blocks if not b.name.startswith("*")]
        dim_styles = [ds.dxf.name for ds in doc.dimstyles]
        entity_counts: dict[str, int] = {}
        text_heights: list[float] = []
        for entity in msp:
            etype = entity.dxftype()
            entity_counts[etype] = entity_counts.get(etype, 0) + 1
            if etype in ("TEXT", "MTEXT"):
                try:
                    h = entity.dxf.height if etype == "TEXT" else entity.dxf.char_height
                    if h and h > 0:
                        text_heights.append(round(h, 4))
                except Exception:
                    pass
        has_title_block = any(
            "title" in b.lower() or "ttlb" in b.lower() or "tb" == b.lower()
            for b in blocks + layers
        )
        return {
            "layers": layers, "blocks": blocks,
            "text_heights": sorted(set(text_heights)),
            "dim_styles": dim_styles, "entity_counts": entity_counts,
            "has_title_block": has_title_block, "source": "ezdxf",
        }
    except Exception as exc:
        log.error("ezdxf failed on %s: %s", path.name, exc)
        return _metadata_only(path)

# ── Deviation detection ───────────────────────────────────────────────────────

STANDARD_TEXT_HEIGHTS = {2.5, 3.0, 3.5, 5.0, 7.0}
AFFECTED_MAP = {
    "Layer Naming":       "templates.py",
    "Dimension Style":    "dxf_builder.py",
    "Title Block":        "blocks.py",
    "Geometry Proportion":"dxf_builder.py",
}


def detect_deviations(drawing_data: dict, standards: dict, path: Path) -> list[dict]:
    proposals: list[dict] = []
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    standard_layer_names: set[str] = set()
    legacy_map: dict[str, str] = {}
    ignore_layers: set[str] = set()

    if standards:
        standard_layer_names = {lay["name"] for lay in standards.get("standard_layers", [])}
        legacy_map   = standards.get("legacy_mappings", {})
        ignore_layers = set(standards.get("ignore_layers", []))

    # 1. Non-standard layer names
    for layer in drawing_data["layers"]:
        if layer in ignore_layers:
            continue
        if standard_layer_names and layer not in standard_layer_names:
            suggestion = legacy_map.get(layer.upper(), None)
            proposal_text = (
                f"Rename layer '{layer}' → '{suggestion}'"
                if suggestion
                else f"Layer '{layer}' has no standard equivalent — consider mapping or removing it"
            )
            proposals.append({
                "timestamp": ts,
                "source_file": str(path.relative_to(ROOT)),
                "category": "Layer Naming",
                "finding": f"Non-standard layer name: '{layer}'",
                "proposal": proposal_text,
                "confidence": 0.85 if suggestion else 0.55,
                "affected_generator": AFFECTED_MAP["Layer Naming"],
            })

    # 2. Unusual text heights
    for h in drawing_data["text_heights"]:
        if h not in STANDARD_TEXT_HEIGHTS and h > 0:
            nearest = min(STANDARD_TEXT_HEIGHTS, key=lambda s: abs(s - h))
            proposals.append({
                "timestamp": ts,
                "source_file": str(path.relative_to(ROOT)),
                "category": "Dimension Style",
                "finding": f"Non-standard text height: {h}mm",
                "proposal": f"Normalise text height from {h}mm to {nearest}mm",
                "confidence": 0.75,
                "affected_generator": AFFECTED_MAP["Dimension Style"],
            })

    # 3. Missing title block
    if not drawing_data["has_title_block"]:
        proposals.append({
            "timestamp": ts,
            "source_file": str(path.relative_to(ROOT)),
            "category": "Title Block",
            "finding": "No title block block-reference or layer detected",
            "proposal": "Insert standard 'C-ANNO-TTLB' title block from blocks.py template",
            "confidence": 0.70,
            "affected_generator": AFFECTED_MAP["Title Block"],
        })

    # 4. Dimension style deviations
    standard_dim_styles = {"Standard", "ISO-25", "BRIDGE_DIM", "COMPACT_ENGINEERING"}
    for ds in drawing_data["dim_styles"]:
        if ds not in standard_dim_styles:
            proposals.append({
                "timestamp": ts,
                "source_file": str(path.relative_to(ROOT)),
                "category": "Dimension Style",
                "finding": f"Non-standard dimension style: '{ds}'",
                "proposal": f"Replace dim style '{ds}' with 'COMPACT_ENGINEERING'",
                "confidence": 0.65,
                "affected_generator": AFFECTED_MAP["Dimension Style"],
            })

    # Deduplicate
    seen: set[tuple] = set()
    unique: list[dict] = []
    for p in proposals:
        key = (p["category"], p["finding"])
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return unique

# ── Proposal I/O ──────────────────────────────────────────────────────────────

def save_proposal_json(proposals: list[dict]) -> Path:
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    out_path = PROPOSALS_DIR / f"{ts}.json"
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(proposals, fh, indent=2)
    return out_path


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def print_proposal(p: dict) -> None:
    print("\n" + "═" * 64)
    print("  💡 REFINEMENT PROPOSAL")
    print("═" * 64)
    print(f"  Timestamp : {p['timestamp']}")
    print(f"  Source    : {p['source_file']}")
    print(f"  Category  : {p['category']}")
    print(f"  Finding   : {p['finding']}")
    print(f"  Proposal  : {p['proposal']}")
    print(f"  Confidence: {p['confidence']:.0%}")
    print(f"  Generator : {p['affected_generator']}")
    print("═" * 64)


def prompt_user(proposal: dict) -> str:
    while True:
        try:
            answer = input("  Accept this refinement? (y/N/skip): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return "skip"
        if answer in ("y", "yes"):
            return "y"
        if answer in ("n", "no", ""):
            return "n"
        if answer == "skip":
            return "skip"
        print("  Please enter y, N, or skip.")

# ── Research log ──────────────────────────────────────────────────────────────

def append_research_log(cycle_summary: dict) -> None:
    DAEMON_DIR.mkdir(parents=True, exist_ok=True)
    ts = cycle_summary["timestamp"]
    lines = [
        f"\n## Cycle — {ts}\n",
        f"- **Files scanned**: {cycle_summary['total_files']} across {cycle_summary['folder_count']} folders\n",
    ]
    for folder, count in cycle_summary["per_folder"].items():
        lines.append(f"  - `{folder}`: {count} DXF files\n")
    lines.append(f"- **Files studied**: {', '.join(cycle_summary['studied']) or 'none'}\n")
    lines.append(f"- **Proposals generated**: {cycle_summary['proposals_generated']}\n")
    lines.append(
        f"- **Accepted**: {cycle_summary['accepted']}  |  "
        f"**Rejected**: {cycle_summary['rejected']}  |  "
        f"**Skipped**: {cycle_summary['skipped']}\n"
    )
    if cycle_summary.get("proposal_file"):
        lines.append(f"- **Saved to**: `{cycle_summary['proposal_file']}`\n")
    with RESEARCH_LOG.open("a", encoding="utf-8") as fh:
        fh.writelines(lines)

# ── Scan helpers ──────────────────────────────────────────────────────────────

def scan_folders() -> tuple[dict[str, list[Path]], int]:
    result: dict[str, list[Path]] = {}
    total = 0
    for folder in SOURCE_FOLDERS:
        label = folder.name
        if not folder.exists():
            log.warning("Source folder not found: %s", folder)
            result[label] = []
            continue
        dxf_files = list(folder.rglob("*.dxf")) + list(folder.rglob("*.DXF"))
        result[label] = dxf_files
        total += len(dxf_files)
        log.info("  %-40s → %d DXF files", label, len(dxf_files))
    return result, total

# ── Main cycle ────────────────────────────────────────────────────────────────

def run_cycle(dry_run: bool = False) -> None:
    log.info("━" * 60)
    log.info("🔍 Research cycle — %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    standards = load_layer_standards()
    folder_map, total_files = scan_folders()

    all_files: list[Path] = [f for files in folder_map.values() for f in files]
    sample = random.sample(all_files, min(MAX_FILES_TO_STUDY, len(all_files))) if all_files else []

    if not sample:
        log.info("No DXF files found in any source folder — skipping study phase.")

    all_proposals: list[dict] = []
    studied_names: list[str] = []

    for path in sample:
        log.info("📐 Studying: %s", path.name)
        studied_names.append(path.name)
        drawing_data = analyze_dxf(path)
        deviations   = detect_deviations(drawing_data, standards, path)
        log.info("   → %d deviation(s) found", len(deviations))
        all_proposals.extend(deviations)

    proposal_file: str | None = None
    if all_proposals:
        saved_path    = save_proposal_json(all_proposals)
        proposal_file = str(saved_path.relative_to(ROOT))
        log.info("💾 Proposals saved: %s", proposal_file)

    accepted = rejected = skipped = 0

    for proposal in all_proposals:
        print_proposal(proposal)
        if dry_run:
            log.info("[dry-run] Skipping prompt.")
            skipped += 1
            continue
        answer = prompt_user(proposal)
        if answer == "y":
            append_jsonl(ACCEPTED_FILE, proposal)
            accepted += 1
            print("  ✅ Accepted and saved.\n")
        elif answer == "n":
            append_jsonl(REJECTED_FILE, proposal)
            rejected += 1
            print("  ❌ Rejected and logged.\n")
        else:
            skipped += 1
            print("  ⏭  Skipped.\n")

    append_research_log({
        "timestamp":           datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "folder_count":        len(SOURCE_FOLDERS),
        "total_files":         total_files,
        "per_folder":          {label: len(files) for label, files in folder_map.items()},
        "studied":             studied_names,
        "proposals_generated": len(all_proposals),
        "accepted":            accepted,
        "rejected":            rejected,
        "skipped":             skipped,
        "proposal_file":       proposal_file,
    })

    log.info(
        "✔ Cycle complete — %d proposals | %d accepted | %d rejected | %d skipped",
        len(all_proposals), accepted, rejected, skipped,
    )

# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ETERNAL_RESEARCH_CHILD — CAD drawing research daemon"
    )
    parser.add_argument("--once",    action="store_true",
                        help="Run a single scan cycle and exit")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show proposals without prompting for acceptance")
    args = parser.parse_args()

    DAEMON_DIR.mkdir(parents=True, exist_ok=True)
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)

    if not RESEARCH_LOG.exists():
        with RESEARCH_LOG.open("w", encoding="utf-8") as fh:
            fh.write("# ETERNAL_RESEARCH_CHILD — Research Log\n\n")
            fh.write("_Auto-generated by research_daemon.py_\n")

    if args.once or args.dry_run:
        run_cycle(dry_run=args.dry_run)
        return

    log.info("🚀 Daemon started — scanning every %d minutes. Ctrl+C to stop.",
             SCAN_INTERVAL_SECONDS // 60)
    try:
        while True:
            run_cycle(dry_run=False)
            log.info("💤 Sleeping %d minutes until next cycle…", SCAN_INTERVAL_SECONDS // 60)
            time.sleep(SCAN_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        log.info("🛑 Daemon stopped by user.")


if __name__ == "__main__":
    main()
