"""
apply_reference_dxf_style.py
==============================
Copy layer colours, linetypes, lineweights and plot flags from a reference
DXF archive onto generated DXF files.

Usage
-----
  pip install ezdxf
  python apply_reference_dxf_style.py <ref_dir> <input> [output_dir]

Arguments
---------
  ref_dir    Folder that contains the reference .dxf files
             (e.g. DRAWINGS_FROM_RAJKUMAR_DESIGNS/)
  input      A single .dxf file  OR  a folder of .dxf files to restyle
  output_dir (optional) Destination folder.
             Omitted → writes <name>_styled.dxf next to each source file.

Exit codes:  0 = all OK,  1 = some files failed,  2 = bad arguments / setup.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Optional

import ezdxf
from ezdxf import recover

# ── logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(levelname)-8s %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# ── types ──────────────────────────────────────────────────────────────────────

# (aci_color, true_color|None, linetype_name, lineweight, plot_flag)
LayerStyle = tuple[int, Optional[int], str, int, int]
StyleMap   = dict[str, LayerStyle]          # key = UPPER-CASE layer name


# ── DXF reading — tolerant, three fall-back strategies ───────────────────────

def _is_int(s: str) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


def _join_split_text(lines: list[str]) -> list[str]:
    """Re-join group-code-1 values that were split across lines by some exporters."""
    out: list[str] = []
    i = 0
    while i < len(lines):
        out.append(lines[i])
        if i + 1 >= len(lines):
            break
        if lines[i].strip() == "1":
            # accumulate continuation lines (non-integer = not a group code)
            parts = [lines[i + 1].rstrip("\r\n")]
            i += 2
            while i < len(lines) and not _is_int(lines[i].strip()):
                parts.append(lines[i].rstrip("\r\n"))
                i += 1
            out.append(" ".join(parts) + "\n")
            continue
        out.append(lines[i + 1])
        i += 2
    return out


def _inject_lwpolyline_subclass(src: Path) -> Path:
    """
    Some older exporters omit the AcDbEntity / AcDbPolyline subclass markers
    that ezdxf needs.  Inject them and write a temp file.
    """
    raw   = src.read_text(encoding="utf-8", errors="surrogateescape")
    lines = _join_split_text(raw.splitlines(keepends=True))

    out: list[str] = []
    handle = 0xA000
    i = 0
    while i < len(lines):
        if (
            lines[i].strip() == "0"
            and i + 1 < len(lines)
            and lines[i + 1].strip() == "LWPOLYLINE"
        ):
            out += [lines[i], lines[i + 1]]
            i += 2
            # Only patch if the next group code is the layer (8), not a handle (5)
            if i < len(lines) and lines[i].strip() == "8":
                out += [" 5\n", f"{handle:X}\n", "100\n", "AcDbEntity\n"]
                handle += 1
                while i < len(lines):
                    out.append(lines[i])
                    if lines[i].strip() == "6" and i + 1 < len(lines):
                        out.append(lines[i + 1])
                        i += 2
                        out += ["100\n", "AcDbPolyline\n"]
                        break
                    i += 1
            continue
        out.append(lines[i])
        i += 1

    tmp = src.with_suffix(".~tmp_patched.dxf")
    tmp.write_text("".join(out), encoding="utf-8", errors="surrogateescape")
    return tmp


def read_dxf(path: Path) -> ezdxf.document.Drawing:
    """
    Read a DXF file with three successive strategies:
      1. Normal ezdxf.readfile
      2. Patch LWPOLYLINE subclass markers → recover.readfile
      3. Raw recover.readfile on original
    Raises the last exception if all three fail.
    """
    # strategy 1
    try:
        return ezdxf.readfile(str(path))
    except Exception:
        pass

    # strategy 2
    tmp: Optional[Path] = None
    try:
        tmp = _inject_lwpolyline_subclass(path)
        doc, _ = recover.readfile(str(tmp))
        return doc
    except Exception:
        pass
    finally:
        if tmp and tmp.exists():
            tmp.unlink(missing_ok=True)

    # strategy 3
    doc, _ = recover.readfile(str(path))
    return doc


# ── DXF R12 handle repair ─────────────────────────────────────────────────────

def _fix_missing_handles(doc) -> int:
    """
    Walk all block-owned entities and ensure each has a valid handle
    registered in the entity database.  DXF R12 files store entities
    without handles; ezdxf cannot *save* such documents unless every
    entity has one.
    """
    db    = doc.entitydb
    fixed = 0

    for block in doc.blocks:
        for entity in list(block):           # list() avoids mutation issues
            needs_fix = False
            try:
                h = entity.dxf.handle
                if not h or h == "0" or h not in db:
                    needs_fix = True
            except Exception:
                needs_fix = True

            if needs_fix:
                try:
                    new_handle = db.handles.next()
                    entity.dxf.handle = new_handle
                    db[new_handle] = entity
                    fixed += 1
                except Exception:
                    pass

    if fixed:
        log.debug("Assigned handles to %d handle-less entities", fixed)
    return fixed


# ── reference style extraction ────────────────────────────────────────────────

def _layer_style(layer) -> LayerStyle:
    dxf = layer.dxf
    return (
        dxf.color,
        dxf.true_color if dxf.hasattr("true_color") else None,
        dxf.linetype,
        dxf.lineweight,
        dxf.plot if dxf.hasattr("plot") else 1,
    )


def build_style_map(ref_dir: Path) -> tuple[StyleMap, Optional[object]]:
    """
    Walk ref_dir, read every .dxf, merge all layer styles into one map.
    Returns (style_map, best_reference_doc).
    best_reference_doc is the file that had the most layers — used for
    linetype copying.
    """
    style_map: StyleMap = {}
    best_doc   = None
    best_count = -1

    dxf_files = sorted(ref_dir.rglob("*.dxf"))
    if not dxf_files:
        log.warning("No .dxf files found in reference folder: %s", ref_dir)
        return style_map, best_doc

    for fpath in dxf_files:
        try:
            doc = read_dxf(fpath)
        except Exception as exc:
            log.warning("Reference skip — %s: %s", fpath.name, exc)
            continue

        n = sum(1 for _ in doc.layers)
        if n > best_count:
            best_count = n
            best_doc   = doc

        for layer in doc.layers:
            style_map[layer.dxf.name.upper()] = _layer_style(layer)

    log.info("Reference: %d unique layers from %s", len(style_map), ref_dir)
    return style_map, best_doc


# ── style application ─────────────────────────────────────────────────────────

def copy_linetypes(target, source) -> None:
    """Copy non-standard linetypes from source doc into target doc."""
    if source is None:
        return
    for lt in source.linetypes:
        name = lt.dxf.name
        if name in ("BYBLOCK", "BYLAYER") or target.linetypes.has_entry(name):
            continue
        desc = lt.dxf.description
        pat  = getattr(lt, "pattern", None)
        try:
            target.linetypes.add(name, pattern=pat, description=desc) if pat \
                else target.linetypes.add(name, description=desc)
        except Exception:
            try:
                target.linetypes.add(name, description=desc)
            except Exception as exc:
                log.debug("Linetype %s not copied: %s", name, exc)


def apply_styles(doc, style_map: StyleMap) -> int:
    """Apply reference styles to matching layers.  Returns count of layers changed."""
    changed = 0
    for layer in doc.layers:
        key = layer.dxf.name.upper()
        if key not in style_map:
            continue
        color, true_color, linetype, lineweight, plot = style_map[key]
        dxf = layer.dxf
        dxf.color      = color
        dxf.lineweight = lineweight
        if true_color is not None and dxf.hasattr("true_color"):
            try:
                dxf.true_color = true_color
            except Exception:
                pass
        try:
            dxf.linetype = linetype
        except Exception:
            dxf.linetype = "CONTINUOUS"
        if dxf.hasattr("plot"):
            dxf.plot = plot
        changed += 1
    return changed


def process(src: Path, style_map: StyleMap, ref_doc, dst: Path) -> bool:
    """Restyle one DXF file and save to dst.  Returns True on success."""
    try:
        doc = read_dxf(src)
        _fix_missing_handles(doc)
        doc.audit()                      # structural repair pass
        copy_linetypes(doc, ref_doc)
        n = apply_styles(doc, style_map)
        dst.parent.mkdir(parents=True, exist_ok=True)
        doc.saveas(str(dst))
        log.info("OK  %-40s → %-30s (%d layers styled)", src.name, dst.name, n)
        return True
    except Exception as exc:
        log.error("FAIL %-40s %s", src.name, exc)
        return False


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)

    ref_dir = Path(sys.argv[1])
    inp     = Path(sys.argv[2])
    out_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    if not ref_dir.is_dir():
        log.error("Reference folder not found: %s", ref_dir)
        sys.exit(2)
    if not inp.exists():
        log.error("Input not found: %s", inp)
        sys.exit(2)

    style_map, ref_doc = build_style_map(ref_dir)
    if not style_map:
        log.error("No layer styles extracted from reference folder — aborting.")
        sys.exit(1)

    targets  = [inp] if inp.is_file() else sorted(inp.rglob("*.dxf"))
    if not targets:
        log.error("No .dxf files found in %s", inp)
        sys.exit(2)

    ok = fail = 0
    for src in targets:
        if out_dir:
            rel = src.relative_to(inp) if inp.is_dir() else Path(src.name)
            dst = out_dir / rel
        else:
            dst = src.with_stem(src.stem + "_styled")

        if process(src, style_map, ref_doc, dst):
            ok += 1
        else:
            fail += 1

    log.info("Done — %d OK, %d failed", ok, fail)
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
