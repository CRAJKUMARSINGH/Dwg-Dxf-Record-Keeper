"""
Bridge CAD Parametric Generator — Streamlit Dashboard
======================================================
Interactive dashboard for generating standardized bridge DXF drawings.
"""

import streamlit as st
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.components import BridgeParameters
from generators.templates import SheetTemplates

st.set_page_config(page_title="Bridge CAD Generator", layout="wide")

st.title("🏗️ Bridge CAD Parametric Generator")
st.markdown("Generate standardized, layered Bridge DXF drawings with sloping terrain, "
            "professional title blocks, and full NSL-aware substructure.")

# Reset Button
col_reset, col_spacer = st.columns([1, 5])
with col_reset:
    if st.button("🔄 Reset to Defaults"):
        st.session_state.clear()
        st.rerun()

# ── Excel Upload ─────────────────────────────────────────────────────────────
with st.expander("📂 Upload Excel from Bridge GAD App (optional)", expanded=False):
    uploaded = st.file_uploader(
        "Upload Excel with VALUE, VARIABLE, DESCRIPTION columns",
        type=["xlsx", "xls"], key="excel_upload"
    )
    if uploaded:
        try:
            df = pd.read_excel(uploaded, header=None)
            df.columns = ["Value", "Variable", "Description"][:len(df.columns)]
            var_dict = df.set_index("Variable")["Value"].to_dict()

            # Map known columns to session state
            mapping = {
                "spans": ("NSPAN", int, 3),
                "span": ("SPAN1", float, 14.0),
                "width": ("CCBR", float, 7.5),
                "slab_thick": ("SLBTHE", float, 0.45),
                "pier_width": ("PIERTW", float, 1.2),
                "futw": ("FUTW", float, 4.0),
                "futd": ("FUTD", float, 2.0),
                "rtl": ("RTL", float, 100.5),
                "datum": ("DATUM", float, 85.0),
            }
            for key, (var_name, dtype, default) in mapping.items():
                if var_name in var_dict:
                    st.session_state[key] = dtype(var_dict[var_name])

            st.success(f"✅ Loaded {len(var_dict)} parameters from Excel")
            st.dataframe(df.head(15), use_container_width=True)
        except Exception as e:
            st.error(f"Failed to parse Excel: {e}")

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "General", "Spans & Deck", "Substructure", "Foundation", "Levels (NSL)", "Generate Outputs"
])

with tab1:
    st.header("General Project Information")
    project_name = st.text_input("Project Name", "Standard Bridge Project", key="project_name")
    drawing_no = st.text_input("Drawing Number", "GAD-001", key="drawing_no")
    client = st.text_input("Client Name", "Client Name", key="client")
    consultant = st.text_input("Consultant Name", "Consultant Name", key="consultant")
    engineer_name = st.text_input("Design Engineer", "Design Engineer", key="engineer_name")
    st.info("ℹ️ Drawing Scale is automatically calculated (1:100, 1:200, etc.) based on bridge dimensions.")
    scale = "Auto"

with tab2:
    st.header("Spans & Deck Slab (Superstructure)")
    colA, colB = st.columns(2)
    with colA:
        spans = st.number_input("NSPAN (Number of Spans)", value=3, step=1, min_value=1, key="spans")
        span = st.number_input("SPAN (Clear Span Length in m)", value=14.0, step=0.5, key="span")
        skew = st.number_input("Skew Angle (°)", value=0.0, step=5.0, key="skew")
    with colB:
        width = st.number_input("CCBR (Carriageway Width in m)", value=7.5, step=0.5, key="width")
        slab_thick = st.number_input("SLBTHE (Slab Thickness in m)", value=0.45, step=0.05, key="slab_thick")
        wear_coat = st.number_input("Wearing Coat Thickness (m)", value=0.075, step=0.005, key="wear_coat")

with tab3:
    st.header("Pier & Abutment (Substructure)")
    colC, colD = st.columns(2)
    with colC:
        st.subheader("Pier Details")
        pier_width = st.number_input("PIERTW (Pier Top Width in m)", value=1.2, step=0.1, key="pier_width")
        pier_cap_width = st.number_input("Pier Cap Width (m)", value=2.5, step=0.1, key="pier_cap_width")
        pier_cap_height = st.number_input("Pier Cap Height (m)", value=0.5, step=0.1, key="pier_cap_height")
    with colD:
        st.subheader("Abutment Details")
        abut_type = st.selectbox("Abutment Type", ["Cantilever", "Counterfort", "Gravity"], key="abut_type")
        abut_top = st.number_input("Abutment Top Width (m)", value=1.5, step=0.1, key="abut_top")

        if abut_type == "Gravity":
            col_go1, col_go2 = st.columns(2)
            abut_h_off = col_go1.number_input("Heel Offset (m)", value=0.5, step=0.1, key="abut_h_off")
            abut_t_off = col_go2.number_input("Toe Offset (m)", value=0.5, step=0.1, key="abut_t_off")
            abut_bot = abut_top + abut_h_off + abut_t_off
            abut_stem = 1.0; abut_toe = 1.5; abut_heel = 2.5; abut_cf = 3.0; abut_batter = 10.0
        else:
            abut_h_off = 0.5; abut_t_off = 0.5; abut_bot = abut_top
            abut_stem = st.number_input("Stem Thickness (m)", value=1.0, step=0.1, key="abut_stem")
            col_toe, col_heel = st.columns(2)
            abut_toe = col_toe.number_input("Toe Length (m)", value=1.5, step=0.1, key="abut_toe")
            abut_heel = col_heel.number_input("Heel Length (m)", value=2.5, step=0.1, key="abut_heel")
            if abut_type == "Counterfort":
                abut_cf = st.number_input("Counterfort Spacing (m)", value=3.0, step=0.5, key="abut_cf")
            else:
                abut_cf = 3.0
            abut_batter = 10.0

    st.subheader("Wing Wall")
    col_ww1, col_ww2, col_ww3 = st.columns(3)
    ww_length = col_ww1.number_input("Wing Wall Length (m)", value=3.0, step=0.5, key="ww_length")
    ww_thick = col_ww2.number_input("Wing Wall Thickness (m)", value=0.45, step=0.05, key="ww_thick")
    ww_angle = col_ww3.number_input("Splay Angle (°)", value=45.0, step=5.0, key="ww_angle")

with tab4:
    st.header("Foundation")
    found_type = st.selectbox("Foundation Type", ["Open Foundation", "Pile Cap"], key="found_type")
    col_fw, col_fd = st.columns(2)
    futw = col_fw.number_input("FUTW (Foundation Width in m)", value=4.0, step=0.5, key="futw")
    futd = col_fd.number_input("FUTD (Foundation Depth below NSL in m)", value=2.0, step=0.5, key="futd")
    found_thick = st.number_input("Foundation/Raft Thickness (m)", value=1.5, step=0.1, key="found_thick")
    pcc_off = st.number_input("PCC Offset (m)", value=0.150, step=0.05, key="pcc_off")
    if found_type == "Pile Cap":
        col_pd, col_pdep = st.columns(2)
        pile_diam = col_pd.number_input("Pile Diameter (m)", value=1.0, step=0.1, key="pile_diam")
        pile_depth = col_pdep.number_input("Pile Depth (m)", value=15.0, step=1.0, key="pile_depth")
    else:
        pile_diam = 1.0; pile_depth = 15.0

with tab5:
    st.header("Levels & Topography")
    st.markdown("*Foundation and Substructure heights are calculated relative to these levels.*")
    colE, colF = st.columns(2)
    with colE:
        rtl = st.number_input("RTL (Road Top Level)", value=100.5, step=0.1, key="rtl")
        hfl = st.number_input("HFL (High Flood Level)", value=98.2, step=0.1, key="hfl")
        datum = st.number_input("DATUM (Reference Level)", value=85.0, step=1.0, key="datum")
    with colF:
        nsl_l = st.number_input("NSL_L (NSL at Left Abutment)", value=100.0, step=0.1, key="nsl_l")
        nsl_c = st.number_input("NSL_C (NSL at Central Pier)", value=99.5, step=0.1, key="nsl_c")
        nsl_r = st.number_input("NSL_R (NSL at Right Abutment)", value=99.8, step=0.1, key="nsl_r")

    assume_slope = st.checkbox("Assume Linear Slope between NSL points", value=True, key="assume_slope")

with tab6:
    st.header("Generate Outputs")
    st.markdown("Select the components to generate:")

    col_cb1, col_cb2 = st.columns(2)
    with col_cb1:
        gen_gad = st.checkbox("General Arrangement Drawing (GAD)", value=True)
        gen_pier = st.checkbox("Pier Details", value=True)
        gen_deck = st.checkbox("Deck Slab Details", value=True)
    with col_cb2:
        gen_wing = st.checkbox("Wing Wall Details", value=True)
        gen_abut = st.checkbox("Abutment Details", value=True)

    col_btn1, col_btn2 = st.columns(2)
    generate_selected = col_btn1.button("🔧 Generate Selected", type="primary")
    generate_all = col_btn2.button("⚡ Generate ALL Drawings")

    if generate_selected or generate_all:
        params = BridgeParameters(
            project_name=project_name, drawing_no=drawing_no, client=client,
            consultant=consultant, engineer_name=engineer_name, scale=scale,
            number_of_spans=spans, span_length=span, carriage_width=width,
            skew_angle=skew, slab_thickness=slab_thick,
            wearing_coat_thickness=wear_coat,
            pier_width=pier_width, pier_cap_width=pier_cap_width,
            pier_cap_height=pier_cap_height,
            abutment_type=abut_type, abutment_top_width=abut_top,
            abutment_bottom_width=abut_bot,
            gravity_heel_offset=abut_h_off, gravity_toe_offset=abut_t_off,
            pcc_offset=pcc_off,
            abutment_stem_thickness=abut_stem,
            abutment_toe_length=abut_toe, abutment_heel_length=abut_heel,
            abutment_counterfort_spacing=abut_cf,
            wing_wall_length=ww_length, wing_wall_thickness=ww_thick,
            wing_wall_splay_angle=ww_angle,
            foundation_type=found_type, futw=futw, futd=futd,
            foundation_thickness=found_thick,
            pile_diameter=pile_diam, pile_depth=pile_depth,
            rtl=rtl, hfl=hfl, datum=datum,
            nsl_left=nsl_l, nsl_center=nsl_c, nsl_right=nsl_r,
            assume_linear_slope=assume_slope,
        )

        output_dir = Path(__file__).resolve().parent.parent / "output" / "dashboard"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Determine what to generate
        if generate_all:
            gen_gad = gen_pier = gen_deck = gen_wing = gen_abut = True

        with st.spinner("Generating Professional CAD Files..."):
            generated_files = []

            if gen_gad:
                b = SheetTemplates.generate_gad(params)
                p = output_dir / "GAD_Generated.dxf"
                b.save(p)
                generated_files.append(("GAD", p))

            if gen_pier:
                b = SheetTemplates.generate_pier_details(params)
                p = output_dir / "Pier_Details_Generated.dxf"
                b.save(p)
                generated_files.append(("Pier Details", p))

            if gen_deck:
                b = SheetTemplates.generate_deck_slab_details(params)
                p = output_dir / "Deck_Slab_Generated.dxf"
                b.save(p)
                generated_files.append(("Deck Slab", p))

            if gen_wing:
                b = SheetTemplates.generate_wing_wall_details(params)
                p = output_dir / "Wing_Wall_Generated.dxf"
                b.save(p)
                generated_files.append(("Wing Wall", p))

            if gen_abut:
                b = SheetTemplates.generate_abutment_details(params)
                p = output_dir / "Abutment_Details_Generated.dxf"
                b.save(p)
                generated_files.append(("Abutment Details", p))

        st.success(f"✅ Generated {len(generated_files)} drawings with terrain slope, "
                   f"NSL levels, and professional title blocks.")

        for name, path in generated_files:
            with open(path, "rb") as file:
                st.download_button(
                    label=f"⬇️ Download {name} (DXF)",
                    data=file,
                    file_name=path.name,
                    mime="application/dxf"
                )

        st.info(f"📁 Files saved to: `{output_dir}`\n\n"
                "💡 To convert DXF to DWG, open in AutoCAD or use ODA File Converter.")
