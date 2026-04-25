import streamlit as st
import sys
from pathlib import Path

# Add current dir to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.components import BridgeParameters
from generators.templates import SheetTemplates

st.set_page_config(page_title="Bridge CAD Generator", layout="wide")

st.title("🏗️ Bridge CAD Parametric Generator")
st.markdown("Instantly generate standardized, layered Bridge DXF drawings matching the `Bridge_GAD_Yogendra_Borse` parameters.")

# Add Reset Button at the top
if st.button("Reset to Defaults"):
    st.session_state.clear()
    st.rerun()

# Layout using Tabs for logical grouping
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
    st.info("ℹ️ Drawing Scale is now automatically calculated (1:100, 1:200, etc.) based on bridge length.")
    # No longer needed as input but kept for state if necessary
    scale = "Auto"

with tab2:
    st.header("Spans & Deck Slab (Superstructure)")
    colA, colB = st.columns(2)
    with colA:
        spans = st.number_input("NSPAN (Number of Spans)", value=3, step=1, min_value=1, key="spans")
        span = st.number_input("SPAN (Clear/Effective Span Length in m)", value=14.0, step=0.5, key="span")
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
            abut_h_off = 0.5; abut_t_off = 0.5;
            abut_bot = abut_top
            abut_stem = st.number_input("Stem Thickness (m)", value=1.0, step=0.1, key="abut_stem")
            col_toe, col_heel = st.columns(2)
            abut_toe = col_toe.number_input("Toe Length (m)", value=1.5, step=0.1, key="abut_toe")
            abut_heel = col_heel.number_input("Heel Length (m)", value=2.5, step=0.1, key="abut_heel")
            
            if abut_type == "Counterfort":
                abut_cf = st.number_input("Counterfort Spacing (m)", value=3.0, step=0.5, key="abut_cf")
            else:
                abut_cf = 3.0
            abut_batter = 10.0

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
        pile_diam = 1.0
        pile_depth = 15.0

with tab5:
    st.header("Levels & Topography")
    st.markdown("*(Foundation and Substructure heights are calculated relative to these levels)*")
    
    colE, colF = st.columns(2)
    with colE:
        rtl = st.number_input("RTL (Road Top Level)", value=100.5, step=0.1, key="rtl")
        hfl = st.number_input("HFL (High Flood Level)", value=98.2, step=0.1, key="hfl")
        datum = st.number_input("DATUM (Reference Level)", value=85.0, step=1.0, key="datum")
    with colF:
        nsl_l = st.number_input("NSL_L (Natural Surface Level at Left Abutment)", value=100.0, step=0.1, key="nsl_l")
        nsl_c = st.number_input("NSL_C (Natural Surface Level at Central Pier)", value=99.5, step=0.1, key="nsl_c")
        nsl_r = st.number_input("NSL_R (Natural Surface Level at Right Abutment)", value=99.8, step=0.1, key="nsl_r")

with tab6:
    st.header("Generate Outputs")
    st.markdown("Select the components you wish to generate:")
    gen_gad = st.checkbox("General Arrangement Drawing (GAD)", value=True)
    gen_pier = st.checkbox("Pier Details", value=True)
    gen_deck = st.checkbox("Deck Slab Details", value=True)
    
    if st.button("Generate Drawings", type="primary"):
        # Compile parameters
        params = BridgeParameters(
            project_name=project_name,
            drawing_no=drawing_no,
            client=client,
            consultant=consultant,
            engineer_name=engineer_name,
            scale=scale,
            number_of_spans=spans,
            span_length=span,
            carriage_width=width,
            skew_angle=skew,
            slab_thickness=slab_thick,
            wearing_coat_thickness=wear_coat,
            pier_width=pier_width,
            pier_cap_width=pier_cap_width,
            pier_cap_height=pier_cap_height,
            abutment_type=abut_type,
            abutment_top_width=abut_top,
            abutment_bottom_width=abut_bot,
            gravity_heel_offset=abut_h_off,
            gravity_toe_offset=abut_t_off,
            pcc_offset=pcc_off,
            abutment_stem_thickness=abut_stem,
            abutment_toe_length=abut_toe,
            abutment_heel_length=abut_heel,
            abutment_counterfort_spacing=abut_cf,
            foundation_type=found_type,
            futw=futw,
            futd=futd,
            foundation_thickness=found_thick,
            pile_diameter=pile_diam,
            pile_depth=pile_depth,
            rtl=rtl,
            hfl=hfl,
            datum=datum,
            nsl_left=nsl_l,
            nsl_center=nsl_c,
            nsl_right=nsl_r
        )
        
        output_dir = Path(__file__).resolve().parent.parent / "output" / "dashboard"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with st.spinner("Generating Professional CAD Files..."):
            generated_files = []
            
            if gen_gad:
                b = SheetTemplates.generate_gad(params)
                path = output_dir / "GAD_Generated.dxf"
                b.save(path)
                generated_files.append(("GAD", path))
                
            if gen_pier:
                b = SheetTemplates.generate_pier_details(params)
                path = output_dir / "Pier_Details_Generated.dxf"
                b.save(path)
                generated_files.append(("Pier Details", path))
                
            if gen_deck:
                b = SheetTemplates.generate_deck_slab_details(params)
                path = output_dir / "Deck_Slab_Generated.dxf"
                b.save(path)
                generated_files.append(("Deck Slab", path))
                
        st.success("Generation Complete! Layers, NSL, and Title Blocks applied.")
        
        # Provide download links
        for name, path in generated_files:
            with open(path, "rb") as file:
                st.download_button(
                    label=f"⬇️ Download {name} (DXF)",
                    data=file,
                    file_name=path.name,
                    mime="application/dxf"
                )
                
        st.info("Note: To convert DXF to DWG, open the file in AutoCAD or use the configured ODA File Converter.")
