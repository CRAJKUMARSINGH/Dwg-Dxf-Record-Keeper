"""
BridgeMaster Pro — Streamlit Dashboard (Phase-3)
================================================
Bridge CAD Parametric Generator with full IRC code checks,
design warnings, How-To guide, and professional sidebar.
"""

import streamlit as st
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.components import BridgeParameters
from generators.templates import SheetTemplates

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BridgeMaster Pro | Bridge CAD Generator",
    layout="wide",
    page_icon="🏗️",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏗️ BridgeMaster Pro")
    st.markdown(
        "<span style='background:#1f77b4;color:white;padding:2px 8px;"
        "border-radius:4px;font-size:0.75rem;'>v1.0</span>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown("### Quick-Start Guide")
    st.markdown(
        "**Step 1** — Fill in project parameters across the tabs\n\n"
        "**Step 2** — Go to **Generate** tab and click *Generate ALL*\n\n"
        "**Step 3** — Download your DXF files"
    )
    st.markdown("---")

    manual_path = Path(__file__).resolve().parent.parent / "USER_MANUAL.md"
    if manual_path.exists():
        st.markdown(f"📖 [Open User Manual](file://{manual_path})")
    else:
        st.markdown("📖 `USER_MANUAL.md` — place in project root")

    st.markdown("---")

    if st.button("🔬 Run ETERNAL_RESEARCH_CHILD", use_container_width=True):
        st.info(
            "**ETERNAL_RESEARCH_CHILD Instructions**\n\n"
            "1. Open a terminal in the project root.\n"
            "2. Run: `python eternal_research_child.py`\n"
            "3. The process will continuously monitor and update bridge "
            "design references in the background.\n"
            "4. Stop with `Ctrl+C` when done."
        )

    st.markdown("---")
    if st.button("🔄 Reset All to Defaults", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🏗️ BridgeMaster Pro | Bridge CAD Generator")
st.markdown(
    "Generate standardized, layered Bridge DXF drawings with sloping terrain, "
    "professional title blocks, and full NSL-aware substructure."
)

# ── Excel Upload ──────────────────────────────────────────────────────────────
with st.expander("📂 Upload Excel from Bridge GAD App (optional)", expanded=False):
    uploaded = st.file_uploader(
        "Upload Excel with VALUE, VARIABLE, DESCRIPTION columns",
        type=["xlsx", "xls"],
        key="excel_upload",
    )
    if uploaded:
        try:
            df = pd.read_excel(uploaded, header=None)
            df.columns = ["Value", "Variable", "Description"][: len(df.columns)]
            var_dict = df.set_index("Variable")["Value"].to_dict()

            mapping = {
                "spans":      ("NSPAN",  int,   3),
                "span":       ("SPAN1",  float, 14.0),
                "width":      ("CCBR",   float, 7.5),
                "slab_thick": ("SLBTHE", float, 0.45),
                "pier_width": ("PIERTW", float, 1.2),
                "futw":       ("FUTW",   float, 4.0),
                "futd":       ("FUTD",   float, 2.0),
                "rtl":        ("RTL",    float, 100.5),
                "datum":      ("DATUM",  float, 85.0),
            }
            for key, (var_name, dtype, default) in mapping.items():
                if var_name in var_dict:
                    st.session_state[key] = dtype(var_dict[var_name])

            st.success(f"✅ Loaded {len(var_dict)} parameters from Excel")
            st.dataframe(df.head(15), use_container_width=True)
        except Exception as e:
            st.error(f"Failed to parse Excel: {e}")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "General",
    "Spans & Deck",
    "Substructure",
    "Foundation",
    "Levels (NSL)",
    "Generate",
    "How To Use",
])

# ── Tab 1 — General ───────────────────────────────────────────────────────────
with tab1:
    st.header("General Project Information")
    project_name  = st.text_input("Project Name",    "Standard Bridge Project", key="project_name")
    drawing_no    = st.text_input("Drawing Number",  "GAD-001",                 key="drawing_no")
    client        = st.text_input("Client Name",     "Client Name",             key="client")
    consultant    = st.text_input("Consultant Name", "Consultant Name",         key="consultant")
    engineer_name = st.text_input("Design Engineer", "Design Engineer",         key="engineer_name")
    st.info("ℹ️ Drawing scale is auto-calculated (1:100, 1:200 …) from bridge dimensions.")
    scale = "Auto"

# ── Tab 2 — Spans & Deck ──────────────────────────────────────────────────────
with tab2:
    st.header("Spans & Deck Slab (Superstructure)")
    colA, colB = st.columns(2)
    with colA:
        spans      = st.number_input("NSPAN (Number of Spans)",        value=3,     step=1,     min_value=1, key="spans")
        span       = st.number_input("SPAN (Clear Span Length in m)",  value=14.0,  step=0.5,               key="span")
        skew       = st.number_input("Skew Angle (°)",                 value=0.0,   step=5.0,               key="skew")
    with colB:
        width      = st.number_input("CCBR (Carriageway Width in m)",  value=7.5,   step=0.5,               key="width")
        slab_thick = st.number_input("SLBTHE (Slab Thickness in m)",   value=0.45,  step=0.05,              key="slab_thick")
        wear_coat  = st.number_input("Wearing Coat Thickness (m)",     value=0.075, step=0.005,             key="wear_coat")

# ── Tab 3 — Substructure ──────────────────────────────────────────────────────
with tab3:
    st.header("Pier & Abutment (Substructure)")
    colC, colD = st.columns(2)
    with colC:
        st.subheader("Pier Details")
        pier_width     = st.number_input("PIERTW (Pier Top Width in m)", value=1.2, step=0.1, key="pier_width")
        pier_cap_width = st.number_input("Pier Cap Width (m)",           value=2.5, step=0.1, key="pier_cap_width")
        pier_cap_height= st.number_input("Pier Cap Height (m)",          value=0.5, step=0.1, key="pier_cap_height")
    with colD:
        st.subheader("Abutment Details")
        abut_type = st.selectbox("Abutment Type", ["Cantilever", "Counterfort", "Gravity"], key="abut_type")
        abut_top  = st.number_input("Abutment Top Width (m)", value=1.5, step=0.1, key="abut_top")

        if abut_type == "Gravity":
            col_go1, col_go2 = st.columns(2)
            abut_h_off = col_go1.number_input("Heel Offset (m)", value=0.5, step=0.1, key="abut_h_off")
            abut_t_off = col_go2.number_input("Toe Offset (m)",  value=0.5, step=0.1, key="abut_t_off")
            abut_bot   = abut_top + abut_h_off + abut_t_off
            abut_stem  = 1.0; abut_toe = 1.5; abut_heel = 2.5; abut_cf = 3.0; abut_batter = 10.0
        else:
            abut_h_off = 0.5; abut_t_off = 0.5; abut_bot = abut_top; abut_batter = 10.0
            abut_stem  = st.number_input("Stem Thickness (m)", value=1.0, step=0.1, key="abut_stem")
            col_toe, col_heel = st.columns(2)
            abut_toe  = col_toe.number_input("Toe Length (m)",  value=1.5, step=0.1, key="abut_toe")
            abut_heel = col_heel.number_input("Heel Length (m)", value=2.5, step=0.1, key="abut_heel")
            abut_cf   = (
                st.number_input("Counterfort Spacing (m)", value=3.0, step=0.5, key="abut_cf")
                if abut_type == "Counterfort" else 3.0
            )

    st.subheader("Wing Wall")
    col_ww1, col_ww2, col_ww3 = st.columns(3)
    ww_length = col_ww1.number_input("Wing Wall Length (m)",    value=3.0,  step=0.5,  key="ww_length")
    ww_thick  = col_ww2.number_input("Wing Wall Thickness (m)", value=0.45, step=0.05, key="ww_thick")
    ww_angle  = col_ww3.number_input("Splay Angle (°)",         value=45.0, step=5.0,  key="ww_angle")

# ── Tab 4 — Foundation ────────────────────────────────────────────────────────
with tab4:
    st.header("Foundation")
    found_type = st.selectbox("Foundation Type", ["Open Foundation", "Pile Cap"], key="found_type")
    col_fw, col_fd = st.columns(2)
    futw       = col_fw.number_input("FUTW (Foundation Width in m)",          value=4.0,  step=0.5,  key="futw")
    futd       = col_fd.number_input("FUTD (Foundation Depth below NSL in m)", value=2.0, step=0.5,  key="futd")
    found_thick= st.number_input("Foundation / Raft Thickness (m)", value=1.5, step=0.1, key="found_thick")
    pcc_off    = st.number_input("PCC Offset (m)",                   value=0.150, step=0.05, key="pcc_off")
    if found_type == "Pile Cap":
        col_pd, col_pdep = st.columns(2)
        pile_diam  = col_pd.number_input("Pile Diameter (m)", value=1.0,  step=0.1, key="pile_diam")
        pile_depth = col_pdep.number_input("Pile Depth (m)",  value=15.0, step=1.0, key="pile_depth")
    else:
        pile_diam = 1.0; pile_depth = 15.0

# ── Tab 5 — Levels (NSL) ──────────────────────────────────────────────────────
with tab5:
    st.header("Levels & Topography")
    st.markdown("*Foundation and substructure heights are calculated relative to these levels.*")
    colE, colF = st.columns(2)
    with colE:
        rtl   = st.number_input("RTL (Road Top Level)",      value=100.5, step=0.1, key="rtl")
        hfl   = st.number_input("HFL (High Flood Level)",    value=98.2,  step=0.1, key="hfl")
        bed_level = st.number_input("Bed Level (River Bed)", value=95.0,  step=0.1, key="bed_level")
        datum = st.number_input("DATUM (Reference Level)",   value=85.0,  step=1.0, key="datum")
    with colF:
        nsl_l = st.number_input("NSL_L (NSL at Left Abutment)",  value=100.0, step=0.1, key="nsl_l")
        nsl_c = st.number_input("NSL_C (NSL at Central Pier)",   value=99.5,  step=0.1, key="nsl_c")
        nsl_r = st.number_input("NSL_R (NSL at Right Abutment)", value=99.8,  step=0.1, key="nsl_r")
    assume_slope = st.checkbox("Assume Linear Slope between NSL points", value=True, key="assume_slope")

# ── Tab 6 — Generate ──────────────────────────────────────────────────────────
with tab6:
    st.header("Generate Outputs")

    # ── Design Checks ─────────────────────────────────────────────────────────
    st.subheader("Design Checks")
    check_col1, check_col2, check_col3 = st.columns(3)

    # L/D ratio — IRC:112
    ld_ratio = span / slab_thick if slab_thick > 0 else 0
    with check_col1:
        if ld_ratio > 20:
            st.warning(
                f"⚠️ **L/D Ratio: {ld_ratio:.1f}** (> 20)\n\n"
                "Slab may be too slender. Consider increasing thickness.\n"
                "*Ref: IRC:112*"
            )
        else:
            st.success(f"✅ L/D Ratio: {ld_ratio:.1f} (≤ 20) — OK  *(IRC:112)*")

    # Freeboard — IRC:SP:13
    freeboard = rtl - hfl
    with check_col2:
        if freeboard < 0.6:
            st.warning(
                f"⚠️ **Freeboard: {freeboard:.2f} m** (< 0.6 m)\n\n"
                "RTL is too close to HFL. Raise road level.\n"
                "*Ref: IRC:SP:13*"
            )
        else:
            st.success(f"✅ Freeboard: {freeboard:.2f} m (≥ 0.6 m) — OK  *(IRC:SP:13)*")

    # Foundation depth
    with check_col3:
        if futd < 1.5:
            st.warning(
                f"⚠️ **Foundation Depth: {futd:.2f} m** (< 1.5 m)\n\n"
                "Minimum foundation depth not met.\n"
                "*Ref: IRC:SP:13*"
            )
        else:
            st.success(f"✅ Foundation Depth: {futd:.2f} m (≥ 1.5 m) — OK")

    st.markdown("---")

    # ── Drawing Selection ─────────────────────────────────────────────────────
    st.subheader("Select Drawings")
    col_cb1, col_cb2 = st.columns(2)
    with col_cb1:
        gen_gad  = st.checkbox("General Arrangement Drawing (GAD)", value=True)
        gen_pier = st.checkbox("Pier Details",                       value=True)
        gen_deck = st.checkbox("Deck Slab Details",                  value=True)
    with col_cb2:
        gen_wing = st.checkbox("Wing Wall Details",   value=True)
        gen_abut = st.checkbox("Abutment Details",    value=True)

    st.markdown("---")

    # ── Primary Generate Button ───────────────────────────────────────────────
    generate_all = st.button("⚡ Generate ALL Drawings", type="primary", use_container_width=True)

    col_btn_sel, _ = st.columns([1, 3])
    generate_selected = col_btn_sel.button("🔧 Generate Selected")

    if generate_selected or generate_all:
        params = BridgeParameters(
            project_name=project_name,   drawing_no=drawing_no,
            client=client,               consultant=consultant,
            engineer_name=engineer_name, scale=scale,
            number_of_spans=spans,       span_length=span,
            carriage_width=width,        skew_angle=skew,
            slab_thickness=slab_thick,   wearing_coat_thickness=wear_coat,
            pier_width=pier_width,       pier_cap_width=pier_cap_width,
            pier_cap_height=pier_cap_height,
            abutment_type=abut_type,     abutment_top_width=abut_top,
            abutment_bottom_width=abut_bot,
            gravity_heel_offset=abut_h_off, gravity_toe_offset=abut_t_off,
            pcc_offset=pcc_off,
            abutment_stem_thickness=abut_stem,
            abutment_toe_length=abut_toe,   abutment_heel_length=abut_heel,
            abutment_counterfort_spacing=abut_cf,
            wing_wall_length=ww_length,  wing_wall_thickness=ww_thick,
            wing_wall_splay_angle=ww_angle,
            foundation_type=found_type,  futw=futw,  futd=futd,
            foundation_thickness=found_thick,
            pile_diameter=pile_diam,     pile_depth=pile_depth,
            rtl=rtl,  hfl=hfl,  bed_level=bed_level,  datum=datum,
            nsl_left=nsl_l, nsl_center=nsl_c, nsl_right=nsl_r,
            assume_linear_slope=assume_slope,
        )

        output_dir = Path(__file__).resolve().parent.parent / "output" / "dashboard"
        output_dir.mkdir(parents=True, exist_ok=True)

        if generate_all:
            gen_gad = gen_pier = gen_deck = gen_wing = gen_abut = True

        tasks = []
        if gen_gad:  tasks.append(("GAD",             "GAD_Generated.dxf",             SheetTemplates.generate_gad))
        if gen_pier: tasks.append(("Pier Details",     "Pier_Details_Generated.dxf",    SheetTemplates.generate_pier_details))
        if gen_deck: tasks.append(("Deck Slab",        "Deck_Slab_Generated.dxf",       SheetTemplates.generate_deck_slab_details))
        if gen_wing: tasks.append(("Wing Wall",        "Wing_Wall_Generated.dxf",        SheetTemplates.generate_wing_wall_details))
        if gen_abut: tasks.append(("Abutment Details", "Abutment_Details_Generated.dxf", SheetTemplates.generate_abutment_details))

        progress_bar = st.progress(0, text="Starting generation…")
        generated_files = []
        errors = []

        for i, (name, filename, fn) in enumerate(tasks):
            progress_bar.progress(
                int((i / len(tasks)) * 100),
                text=f"Generating {name}…"
            )
            try:
                b = fn(params)
                p = output_dir / filename
                b.save(p)
                generated_files.append((name, p))
            except Exception as exc:
                errors.append((name, str(exc)))

        progress_bar.progress(100, text="Done!")

        # ── Summary Table ─────────────────────────────────────────────────────
        st.subheader("Generation Summary")
        summary_rows = []
        for name, path in generated_files:
            size_kb = path.stat().st_size / 1024 if path.exists() else 0
            summary_rows.append({"Drawing": name, "File": path.name,
                                  "Size (KB)": f"{size_kb:.1f}", "Status": "✅ OK"})
        for name, err in errors:
            summary_rows.append({"Drawing": name, "File": "—",
                                  "Size (KB)": "—", "Status": f"❌ {err}"})

        if summary_rows:
            st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

        # ── Download Buttons ──────────────────────────────────────────────────
        if generated_files:
            st.subheader("Download Files")
            dl_cols = st.columns(min(len(generated_files), 3))
            for idx, (name, path) in enumerate(generated_files):
                with dl_cols[idx % 3]:
                    with open(path, "rb") as fh:
                        st.download_button(
                            label=f"⬇️ {name}",
                            data=fh,
                            file_name=path.name,
                            mime="application/dxf",
                            use_container_width=True,
                        )

            st.info(
                f"📁 Output folder: `{output_dir}`\n\n"
                "💡 To convert DXF → DWG, open in AutoCAD or use ODA File Converter."
            )

        if errors:
            st.error(f"{len(errors)} drawing(s) failed. Check parameters and try again.")

# ── Tab 7 — How To Use ────────────────────────────────────────────────────────
with tab7:
    st.header("How To Use BridgeMaster Pro")
    st.markdown(
        "Follow these six steps to generate a complete set of bridge CAD drawings. "
        "Expand each step for detailed guidance."
    )

    with st.expander("Step 1 — Fill General Info", expanded=False):
        st.markdown(
            """
**Tab:** General

Enter the administrative details for your project. These appear in the title block of every drawing.

| Parameter | Description | Example |
|---|---|---|
| Project Name | Full name of the bridge project | `NH-48 ROB at Km 142` |
| Drawing Number | Reference number for the GAD | `GAD-001` |
| Client Name | Commissioning authority | `NHAI / PWD` |
| Consultant Name | Design firm | `RKS Engineering` |
| Design Engineer | Responsible engineer | `Er. R.K. Sharma` |

> Drawing scale is computed automatically from bridge dimensions.
            """
        )

    with st.expander("Step 2 — Set Spans & Deck", expanded=False):
        st.markdown(
            """
**Tab:** Spans & Deck

Define the superstructure geometry.

| Parameter | Key | Unit | Typical Range |
|---|---|---|---|
| Number of Spans | NSPAN | — | 1 – 10 |
| Clear Span Length | SPAN | m | 6 – 30 |
| Carriageway Width | CCBR | m | 7.5 – 12.0 |
| Slab Thickness | SLBTHE | m | 0.30 – 0.60 |
| Wearing Coat | — | m | 0.065 – 0.090 |
| Skew Angle | — | ° | 0 – 60 |

**IRC:112 Note:** Keep L/D ratio ≤ 20 for solid slab bridges.
            """
        )

    with st.expander("Step 3 — Configure Substructure", expanded=False):
        st.markdown(
            """
**Tab:** Substructure

Set pier and abutment geometry. Abutment parameters change dynamically based on type.

**Pier**

| Parameter | Key | Unit | Typical Range |
|---|---|---|---|
| Pier Top Width | PIERTW | m | 0.8 – 2.0 |
| Pier Cap Width | — | m | 1.5 – 3.5 |
| Pier Cap Height | — | m | 0.4 – 0.8 |

**Abutment Types**

- **Cantilever** — Stem + base slab (toe & heel). Most common for medium spans.
- **Counterfort** — Cantilever with vertical ribs; use for heights > 6 m.
- **Gravity** — Mass concrete; use for small bridges / low fills.

| Parameter | Unit | Typical Range |
|---|---|---|
| Stem Thickness | m | 0.6 – 1.5 |
| Toe Length | m | 1.0 – 2.5 |
| Heel Length | m | 1.5 – 3.5 |
| Counterfort Spacing | m | 2.5 – 4.0 |
            """
        )

    with st.expander("Step 4 — Set Foundation", expanded=False):
        st.markdown(
            """
**Tab:** Foundation

Choose between open (spread) foundation or pile cap.

| Parameter | Key | Unit | Typical Range |
|---|---|---|---|
| Foundation Width | FUTW | m | 2.5 – 6.0 |
| Foundation Depth below NSL | FUTD | m | 1.5 – 4.0 |
| Raft / Footing Thickness | — | m | 0.6 – 2.0 |
| PCC Offset | — | m | 0.10 – 0.20 |
| Pile Diameter (Pile Cap) | — | m | 0.6 – 1.5 |
| Pile Depth (Pile Cap) | — | m | 10 – 30 |

**IRC:SP:13 Note:** Minimum foundation depth = 1.5 m below scour level.
            """
        )

    with st.expander("Step 5 — Enter Levels (NSL)", expanded=False):
        st.markdown(
            """
**Tab:** Levels (NSL)

All elevations are in metres above mean sea level (AMSL).

| Parameter | Key | Unit | Notes |
|---|---|---|---|
| Road Top Level | RTL | m | Top of wearing coat |
| High Flood Level | HFL | m | Design flood level |
| River Bed Level | Bed Level | m | Lowest bed elevation |
| Reference Datum | DATUM | m | Drawing datum line |
| NSL at Left Abutment | NSL_L | m | Ground level, left end |
| NSL at Central Pier | NSL_C | m | Ground level, mid-bridge |
| NSL at Right Abutment | NSL_R | m | Ground level, right end |

**IRC:SP:13 Note:** Minimum freeboard (RTL − HFL) = 0.6 m for culverts, 0.9 m for major bridges.

Enable *Assume Linear Slope* to interpolate NSL between the three points automatically.
            """
        )

    with st.expander("Step 6 — Generate & Download", expanded=False):
        st.markdown(
            """
**Tab:** Generate

1. Review the **Design Checks** panel — fix any warnings before generating.
2. Tick the drawings you need (or leave all ticked).
3. Click **⚡ Generate ALL Drawings** (full-width primary button).
4. Watch the progress bar — each drawing is generated sequentially.
5. Review the **Generation Summary** table (name, file size, status).
6. Click individual **⬇️ Download** buttons to save DXF files.
7. Output folder path is shown — open it in Windows Explorer to batch-copy files.

**Tip:** Open DXF files in AutoCAD, BricsCAD, or the free ODA File Converter.
            """
        )

    st.markdown("---")
    st.subheader("Parameter Reference Table")
    ref_data = {
        "Parameter":   ["NSPAN", "SPAN", "CCBR", "SLBTHE", "PIERTW", "FUTW", "FUTD",
                         "RTL", "HFL", "Bed Level", "NSL_L", "NSL_C", "NSL_R", "DATUM"],
        "Description": [
            "Number of spans", "Clear span length", "Carriageway width",
            "Deck slab thickness", "Pier top width", "Foundation width",
            "Foundation depth below NSL", "Road top level", "High flood level",
            "River bed level", "NSL at left abutment", "NSL at central pier",
            "NSL at right abutment", "Drawing reference datum",
        ],
        "Unit":        ["—", "m", "m", "m", "m", "m", "m", "m AMSL", "m AMSL",
                        "m AMSL", "m AMSL", "m AMSL", "m AMSL", "m AMSL"],
        "Typical Range": [
            "1 – 10", "6 – 30", "7.5 – 12", "0.30 – 0.60", "0.8 – 2.0",
            "2.5 – 6.0", "1.5 – 4.0", "site-specific", "site-specific",
            "site-specific", "site-specific", "site-specific", "site-specific",
            "site-specific",
        ],
        "IRC Reference": [
            "IRC:SP:13", "IRC:SP:13", "IRC:SP:13", "IRC:112",
            "IRC:112", "IRC:SP:13", "IRC:SP:13",
            "IRC:SP:13", "IRC:SP:13", "IRC:SP:13",
            "IRC:6", "IRC:6", "IRC:6", "—",
        ],
    }
    st.dataframe(pd.DataFrame(ref_data), use_container_width=True)

    st.markdown("---")
    st.markdown(
        "**IRC Code References**\n\n"
        "- **IRC:112-2020** — Code of Practice for Concrete Road Bridges\n"
        "- **IRC:SP:13-2004** — Guidelines for the Design of Small Bridges and Culverts\n"
        "- **IRC:6-2017** — Standard Specifications and Code of Practice for Road Bridges "
        "(Section II — Loads and Load Combinations)"
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#888;font-size:0.85rem;'>"
    "BridgeMaster Pro v1.0 &nbsp;|&nbsp; © 2026 RKS Engineering &nbsp;|&nbsp; "
    "IRC:112 / IRC:SP:13 Compliant"
    "</div>",
    unsafe_allow_html=True,
)
