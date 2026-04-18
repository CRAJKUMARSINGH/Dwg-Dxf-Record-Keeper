# Feature comparison: OUR_APP vs REFERENCE-APP00

**OUR_APP** = this repository (`artifacts/bridge-design-suite`, `artifacts/api-server`, `lib/*`, root tooling).  
**REFERENCE-APP00** = optional local tree `REFERENCE-APP00/` (nested `.git`; listed in `.gitignore`—restore from your backup or ZIP when you need a line-by-line diff again).

| # | Feature / capability | OUR_APP | REFERENCE-APP00 | Status | Action (zero-loss) |
|---|------------------------|---------|-------------------|--------|----------------------|
| 1 | Dashboard + stats API | Yes (`/`, `@workspace/api-client-react`) | No | **Kept** | — |
| 2 | Projects CRUD + UI | Yes | No | **Kept** | — |
| 3 | File library + detail | Yes | No | **Kept** | — |
| 4 | Analysis records + detail | Yes | No | **Kept** | — |
| 5 | Comparisons + detail | Yes | No | **Kept** | — |
| 6 | Scan drawing → parameters API | Yes (`scan-drawing`) | No | **Kept** | — |
| 7 | DXF studio (multi-sheet, client export) | Yes (`/generator`, TS `lib/drawings/*`) | No (server-driven zip) | **Kept** | Optional: add server zip path later |
| 8 | App shell (sidebar, nav, wide studio) | Yes | No (bare `Switch`) | **Kept** | — |
| 9 | Tooltip / Toaster / layout polish | Yes | Partial (no `AppLayout`) | **Kept** | — |
| 10 | Single-page “reckoner” home | Partial (split across dashboard + generator) | Yes (`Home.tsx` only route) | **Absorb** | Port **reference tables** (slab / pier / abutment / bearing / wing wall) + **sample presets** into `/generator` or new `/reckoner` tab without removing existing fields |
| 11 | Drawing catalogue list (001–015 titles) | Partial (9 implemented DRGs) | Yes (static `DRAWINGS_LIST`) | **Absorb** | Add read-only checklist or “roadmap” panel; implement new sheets only when spec matches TS engine |
| 12 | POST `/generate-drawings` → Python `bridge_draw.py` → ZIP | No | Yes (`api-server/routes/generate.ts`) | **New (optional)** | Add route behind **feature flag**; fix `WORKSPACE` paths for Windows + repo root; keep existing APIs default |
| 13 | `bridge_draw.py` (server ezdxf, layer defs, Rajkumar layers) | No (browser DXF) | Yes | **Absorb (optional)** | Document side-by-side with TS generator; merge **layer name / colour** constants only if they improve TS output without API break |
| 14 | `apply_rajkumar_style.py` (layers + **textstyles** + **dimstyles** + **header** vars) | `apply_reference_dxf_style.py` (layers + linetypes; repair bad DXF) | Richer stamp | **Improve** | Extend our script with **textstyle**, **dimstyle**, **header** merge from ref (same safety: no forced entity BYLAYER); keep repair path for broken LWPOLYLINE/TEXT |
| 15 | `params_example.json` + `main.py` CLI | `DEFAULT_BRIDGE_INPUT` + scripts | Overlap | **Kept + doc** | Link example JSON from docs; align field names only if adding server path |
| 16 | Mockup sandbox artifact | Yes | Yes | **Kept** | Optional later: component diff |
| 17 | Drizzle / DB integrations in workspace | Yes | Similar catalog | **Kept** | Bump catalog only when pnpm workspace agrees |

## Summary

- **Nothing in OUR_APP must be removed** to “merge”: REFERENCE-APP00 is a **narrower** product (single UI + zip generator) with **valuable reference data** (tables, drawing list, richer style stamp, optional server pipeline).
- **Highest value, lowest risk:** enrich `apply_reference_dxf_style.py` from `apply_rajkumar_style.py` (textstyles, dimstyles, header); add **reckoner tables + presets** to the existing generator UI.
- **Higher scope, flag-gated:** optional `/generate-drawings` + `bridge_draw.py` for ZIP output, with paths corrected for Windows and repo layout.

## Next step (per your approval workflow)

1. You mark rows in the table: **must absorb now** / **later** / **never**.  
2. Implementation proceeds on branch `feature/hybrid-merge-reference-app00` in small commits per row cluster.
