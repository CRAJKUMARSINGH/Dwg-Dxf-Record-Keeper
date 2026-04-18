# apply_reference_dxf_style.py
import os
import sys
import ezdxf
from ezdxf import recover


def _is_group_code_token(st):
    try:
        int(st)
        return True
    except Exception:
        return False


def _fix_split_text_values(L):
    out = []
    i = 0
    while i < len(L):
        if i + 1 >= len(L):
            out.append(L[i])
            break
        code_line = L[i]
        val_line = L[i + 1]
        code_st = code_line.strip()
        out.append(code_line)
        if code_st == "1":
            parts = [val_line.rstrip("\r\n")]
            i += 2
            while i < len(L):
                peek = L[i].strip()
                if _is_group_code_token(peek):
                    break
                parts.append(L[i].rstrip("\r\n"))
                i += 1
            out.append(" ".join(parts) + "\n")
            continue
        out.append(val_line)
        i += 2
    return out


def _patch_lwpolylines(path):
    with open(path, "rt", encoding="utf-8", errors="surrogateescape") as f:
        L = f.readlines()
    L = _fix_split_text_values(L)
    out = []
    i = 0
    handle = 0xA000
    while i < len(L):
        if L[i].strip() == "0" and i + 1 < len(L) and L[i + 1].strip() == "LWPOLYLINE":
            out.append(L[i])
            out.append(L[i + 1])
            i += 2
            if i < len(L) and L[i].strip() == "8":
                out.append("  5\n")
                out.append("%X\n" % handle)
                handle += 1
                out.append("100\n")
                out.append("AcDbEntity\n")
            while i < len(L):
                out.append(L[i])
                if L[i].strip() == "6" and i + 1 < len(L):
                    out.append(L[i + 1])
                    i += 2
                    out.append("100\n")
                    out.append("AcDbPolyline\n")
                    break
                i += 1
            continue
        out.append(L[i])
        i += 1
    tmp = path + ".~patched"
    with open(tmp, "wt", encoding="utf-8", errors="surrogateescape", newline="") as f:
        f.writelines(out)
    return tmp


def _read_dxf(path):
    try:
        return ezdxf.readfile(path)
    except Exception:
        pass
    patched = None
    try:
        patched = _patch_lwpolylines(path)
        try:
            doc, _aud = recover.readfile(patched)
            return doc
        except Exception:
            doc, _aud = recover.explore(patched)
            return doc
    except Exception:
        pass
    finally:
        if patched:
            try:
                os.remove(patched)
            except Exception:
                pass
    try:
        doc, _aud = recover.readfile(path)
        return doc
    except Exception:
        pass
    doc, _aud = recover.explore(path)
    return doc


def _walk_dxf_paths(root):
    found = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(".dxf"):
                found.append(os.path.join(dirpath, fn))
    return found


def _layer_row(layer):
    d = layer.dxf
    tc = None
    if d.hasattr("true_color"):
        tc = d.true_color
    plot = 1
    if d.hasattr("plot"):
        plot = d.plot
    return (d.color, tc, d.linetype, d.lineweight, plot)


def _pick_ref_docs(ref_root):
    paths = _walk_dxf_paths(ref_root)
    merged = {}
    best_doc = None
    best_count = -1
    for p in paths:
        try:
            doc = _read_dxf(p)
        except Exception:
            continue
        n = 0
        for _ in doc.layers:
            n += 1
        if n > best_count:
            best_count = n
            best_doc = doc
        for layer in doc.layers:
            merged[layer.dxf.name.upper()] = _layer_row(layer)
    return merged, best_doc


def _copy_linetypes(tdoc, sdoc):
    if sdoc is None:
        return
    for lt in sdoc.linetypes:
        name = lt.dxf.name
        if name in ("BYBLOCK", "BYLAYER"):
            continue
        if tdoc.linetypes.has_entry(name):
            continue
        desc = lt.dxf.description
        pat = None
        if hasattr(lt, "pattern"):
            pat = lt.pattern
        try:
            if pat is not None:
                tdoc.linetypes.add(name, pattern=pat, description=desc)
            else:
                tdoc.linetypes.add(name, description=desc)
        except Exception:
            try:
                tdoc.linetypes.add(name, description=desc)
            except Exception:
                pass


def _apply_layers(doc, merged):
    for layer in doc.layers:
        key = layer.dxf.name.upper()
        if key not in merged:
            continue
        color, tc, ltype, lw, plot = merged[key]
        dx = layer.dxf
        dx.color = color
        if tc is not None and dx.hasattr("true_color"):
            try:
                dx.true_color = tc
            except Exception:
                pass
        try:
            dx.linetype = ltype
        except Exception:
            dx.linetype = "CONTINUOUS"
        dx.lineweight = lw
        if dx.hasattr("plot"):
            dx.plot = plot


def _process_one(src_path, merged, refdoc, dst_path):
    doc = _read_dxf(src_path)
    _copy_linetypes(doc, refdoc)
    _apply_layers(doc, merged)
    os.makedirs(os.path.dirname(os.path.abspath(dst_path)) or ".", exist_ok=True)
    doc.saveas(dst_path)


def main():
    if len(sys.argv) < 3:
        sys.exit(2)
    ref_root = sys.argv[1]
    inp = sys.argv[2]
    out_arg = sys.argv[3] if len(sys.argv) > 3 else None
    merged, refdoc = _pick_ref_docs(ref_root)
    if os.path.isfile(inp):
        targets = [inp]
        is_dir = False
    else:
        targets = _walk_dxf_paths(inp)
        is_dir = True
    for tpath in targets:
        if out_arg:
            if is_dir:
                rel = os.path.relpath(tpath, inp)
                dst = os.path.join(out_arg, rel)
            else:
                dst = os.path.join(out_arg, os.path.basename(tpath))
        else:
            d, f = os.path.split(tpath)
            base, ext = os.path.splitext(f)
            dst = os.path.join(d or ".", base + "_chauhan" + ext)
        try:
            _process_one(tpath, merged, refdoc, dst)
        except Exception:
            pass


if __name__ == "__main__":
    main()
