# Dwg-Dxf-Record-Keeper

**Bridge drawing records + DXF studio + API** — monorepo for practising engineers who want **CAD-ready DXF**, a **proper file/record workspace**, and **optional Python** tooling on the same tree.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](package.json)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178c6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![pnpm](https://img.shields.io/badge/pnpm-workspace-f69220?logo=pnpm&logoColor=white)](https://pnpm.io/)

---

## Why open this repo?

- **DXF studio** in the browser — nine IRC-style RCC slab bridge sheets, batch download.  
- **Dashboard** — projects, drawing library, analysis records, comparisons (PostgreSQL + Drizzle).  
- **Scan drawing** — image → structured parameters (when API keys / server are configured).  
- **Python style pass** — `apply_reference_dxf_style.py` aligns layer/linetype tables to your **`DRAWINGS_FROM_RAJKUMAR_DESIGNS/`** archive.  
- **COLLECTION FROM RECORD** — DXF pattern analysis scripts (`GUIDE.md` inside that folder).

---

## Documentation (start here)

| Doc | What |
|-----|------|
| **[docs/USER_MANUAL.md](docs/USER_MANUAL.md)** | Full manual + **video chapter script** for recordings + Streamlit deploy. |
| **[COLLECTION FROM RECORD/GUIDE.md](COLLECTION%20FROM%20RECORD/GUIDE.md)** | Python collection tools only. |
| **[replit.md](replit.md)** | Replit / workspace commands. |

**One-click manual (hosted):** deploy [`streamlit-manual/`](streamlit-manual/) on [Streamlit Cloud](https://streamlit.io/cloud) and set the repo **About → Website** to your app URL.

---

## Quick commands

```bash
pnpm install
pnpm run typecheck
pnpm --filter @workspace/api-server run dev
pnpm --filter @workspace/bridge-design-suite run dev
```

```bash
pip install ezdxf
python apply_reference_dxf_style.py DRAWINGS_FROM_RAJKUMAR_DESIGNS path\to\dxfs path\to\styled_out
```

---

## Repository layout (short)

```
artifacts/bridge-design-suite/   # Main React app
artifacts/api-server/            # Express API
lib/                             # Shared clients + DB
COLLECTION FROM RECORD/          # Python DXF experiments
docs/USER_MANUAL.md              # Human + “video script” guide
streamlit-manual/                # Optional hosted manual UI
apply_reference_dxf_style.py     # DXF post-style from reference folder
```

---

## Star & watch

If this saves you time in bridge documentation and DXF export, **star the repo** and open an **Issue** for bugs or feature requests. Pull requests welcome for the roadmap items in `docs/USER_MANUAL.md` (Appendix A).
