# Dwg-Dxf-Record-Keeper — User Manual

Monorepo for **bridge drawing records**, **DXF generation**, **API-backed workspace**, and **Python analysis tools**.

---

## 1. What is in this repository?

| Area | Path | Purpose |
|------|------|---------|
| Web app (main) | `artifacts/bridge-design-suite` | Dashboard, projects, files, records, comparisons, **DXF studio** (`/generator`). |
| API | `artifacts/api-server` | Express API: stats, CRUD, **scan-drawing** (image → parameters). |
| Shared libraries | `lib/*` | API client, DB, Zod spec. |
| Python DXF style | `apply_reference_dxf_style.py` | Match generated DXF layer/linetype style to `DRAWINGS_FROM_RAJKUMAR_DESIGNS/`. |
| Pattern tools | `COLLECTION FROM RECORD/` | DXF analyzers, demos — see **`COLLECTION FROM RECORD/GUIDE.md`**. |

**Prerequisites:** Node **24+**, **pnpm**, PostgreSQL for full API; **Python 3.11+** with `ezdxf` for style script and collection scripts.

---

## 2. Quick start (web + API)

```bash
cd Dwg-Dxf-Record-Keeper
pnpm install
pnpm run typecheck
pnpm --filter @workspace/api-server run dev
pnpm --filter @workspace/bridge-design-suite run dev
```

Configure API base URL for the web app per your environment (Replit secrets or local `.env` patterns used in your deployment).

---

## 3. DXF studio (browser)

1. Open the Bridge Design Suite app (dev server URL).
2. Go to **DXF studio** (`/generator`).
3. Fill parameters or use **scan** (when API is running).
4. Download generated `.dxf` files.

---

## 4. Post-process DXF style (Python)

From repo root (paths can be relative):

```bash
pip install ezdxf
python apply_reference_dxf_style.py DRAWINGS_FROM_RAJKUMAR_DESIGNS GENERATED_DRAWINGS GENERATED_DRAWINGS_STYLED
```

- **Arg 1:** Reference folder (your archive of final drawings).  
- **Arg 2:** One `.dxf` file or a folder of generated drawings.  
- **Arg 3 (optional):** Output folder; if omitted, writes `*_chauhan.dxf` next to inputs.

---

## 5. Video walkthrough — recording script (chapters)

*These are scene titles and talking points for **you** to record; the repo does not ship video files.*

| Ch. | Length (approx.) | Show / say |
|-----|------------------|------------|
| 0 | 0:30 | Title: “Dwg-Dxf-Record-Keeper — bridge records + DXF studio”. |
| 1 | 2:00 | Clone repo, `pnpm install`, `pnpm run typecheck`. |
| 2 | 2:00 | Start API + web app; open Dashboard (stats, recent files). |
| 3 | 4:00 | Projects → Files → Records → Comparisons (one flow). |
| 4 | 6:00 | **DXF studio**: fill span, RTL/HFL, export 2–3 sheets; show CAD opening DXF. |
| 5 | 3:00 | **Scan drawing**: upload sketch, apply extracted fields (if API configured). |
| 6 | 3:00 | Run `apply_reference_dxf_style.py`; before/after layer table in CAD. |
| 7 | 2:00 | `COLLECTION FROM RECORD`: open `GUIDE.md`, run `run.bat` / demo. |
| 8 | 1:00 | Where to read this manual (`docs/USER_MANUAL.md`) and Streamlit viewer (`streamlit-manual/`). |

**Thumbnail ideas:** bridge elevation line-art; split screen “parameters → DXF”.

---

## 6. Streamlit “User Manual” viewer

Deploy the small app in **`streamlit-manual/`** (renders this file):

1. Push this repo to GitHub.  
2. [Streamlit Community Cloud](https://streamlit.io/cloud) → New app → pick repo → **Main file path:** `streamlit-manual/app.py`.  
3. Python version **3.11** (or match your `requirements.txt`).  
4. App URL: put it in your GitHub **About** website field (see root `README.md`).

---

## Appendix A — Hybrid roadmap (REFERENCE-APP00)

Optional local compare tree: `REFERENCE-APP00/` (gitignored if present).

| # | Capability | Production app | Reference | Action |
|---|------------|----------------|-----------|--------|
| 1–9 | Dashboard, projects, files, records, comparisons, scan, studio shell, polish | Yes | Partial / No | **Kept** |
| 10 | Reckoner tables + presets on one page | Partial | Yes | Absorb into `/generator` when scheduled |
| 11 | 15-title drawing catalogue | Partial | Yes | Roadmap UI |
| 12–13 | Server ZIP via `bridge_draw.py` | No | Yes | Optional flagged route |
| 14 | Richer style (`textstyles`, `dimstyles`, header) | Partial | Yes | Improve `apply_reference_dxf_style.py` |
| 15–17 | Params CLI, mockups, Drizzle | Yes | Overlap | **Kept** |

---

## Appendix B — Support

- **Issues:** use GitHub Issues on this repository.  
- **Security:** supply-chain: `pnpm-workspace.yaml` minimum release age; do not disable without review.
