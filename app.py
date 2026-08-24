import streamlit as st

st.set_page_config(
    page_title="Extremity & Trunk Local Flap Decision Tool", layout="centered"
)

if "step" not in st.session_state:
    st.session_state.step = 1
if "selected_flap_idx" not in st.session_state:
    st.session_state.selected_flap_idx = 0

st.title("Extremity & Trunk Soft Tissue Decision Tool")
st.caption(
    "Clinical Decision Support & Risk Triage for Non-Plastic Surgeons"
)

# ------------------------------------------------------------------
# SCREEN 1: Location & Safety Screening
# ------------------------------------------------------------------
if st.session_state.step == 1:
    st.header("Step 1: Location & Safety Screening")

    subzone = st.selectbox(
        "Select Anatomical Subzone",
        [
            "Upper Arm",
            "Elbow Joint Line (High Tension / Flexion Crease)",
            "Forearm",
            "Hand / Digits (High Complexity Zone)",
            "Anterior Thigh",
            "Posterior Thigh",
            "Knee Joint Line (High Tension / Flexion Crease)",
            "Buttock / Gluteal Region",
            "Proximal / Mid Calf",
            "Distal Leg / Ankle / Foot (High Complexity Zone)",
        ],
    )

    indication = st.radio(
        "Clinical Presentation / Goal",
        [
            "Soft Tissue Hole / Defect (Requires Tissue Coverage)",
            "Linear Scar Contracture / Flexion Line Tension (Requires Length / Strain Relief)",
        ],
    )

    radiation = st.checkbox("Prior Radiation to Wound Site")
    stasis = st.checkbox("Severe Stasis Dermatitis / Severe Edema / Advanced PVD")

    red_flag_zones = [
        "Hand / Digits (High Complexity Zone)",
        "Distal Leg / Ankle / Foot (High Complexity Zone)",
    ]

    if subzone in red_flag_zones or radiation or stasis:
        st.error(
            "🔴 MANDATORY CONSULT REQUIRED (RED FLAG)\n\n"
            "• **Reason:** High-complexity subzone or compromised vascular tissue bed.\n"
            "• **Clinical Action:** Do NOT attempt local random flaps. High risk of total flap failure, neurovascular compromise, or chronic wound non-healing. Contact Plastic / Hand Surgery."
        )
    elif subzone in ["Elbow Joint Line (High Tension / Flexion Crease)", "Knee Joint Line (High Tension / Flexion Crease)"]:
        st.warning(
            "⚠️ HIGH-TENSION JOINT CREASE ZONE\n\n"
            "Wounds crossing flexion lines carry a high risk of dehiscence and joint contracture. "
            "Reconstruction must incorporate strain-relieving designs (e.g., Z-Plasty)."
        )
        if st.button("Proceed to Defect Metrics →"):
            st.session_state.subzone = subzone
            st.session_state.indication = indication
            st.session_state.step = 2
    else:
        if st.button("Next: Defect Metrics →"):
            st.session_state.subzone = subzone
            st.session_state.indication = indication
            st.session_state.step = 2

# ------------------------------------------------------------------
# SCREEN 2: Defect Metrics & Wound Bed Quality
# ------------------------------------------------------------------
elif st.session_state.step == 2:
    st.header("Step 2: Defect Metrics & Bed Quality")

    width = st.number_input("Defect Width (cm)", min_value=0.5, max_value=15.0, value=2.5, step=0.5)
    length = st.number_input("Defect Length / Scar Length (cm)", min_value=0.5, max_value=20.0, value=3.0, step=0.5)

    bed = st.radio(
        "Deep Wound Bed Quality",
        [
            "Healthy Muscle / Intact Subcutaneous Tissue / Granulation",
            "Intact Periosteum or Intact Peritenon",
            "Bare Bone (No Periosteum)",
            "Exposed Tendon (No Peritenon)",
            "Exposed Orthopedic / Vascular Hardware",
        ],
    )

    max_dim = max(width, length)
    unsafe_beds = [
        "Bare Bone (No Periosteum)",
        "Exposed Tendon (No Peritenon)",
        "Exposed Orthopedic / Vascular Hardware",
    ]

    # Subzone-specific size restriction for Mid-Calf
    if st.session_state.subzone == "Proximal / Mid Calf" and max_dim > 2.0:
        st.error(
            "🔴 MANDATORY CONSULT REQUIRED (RED FLAG)\n\n"
            f"• **Reason:** Mid-calf defect size ({max_dim} cm) exceeds the 2.0 cm safety limit for local skin flaps in the leg.\n"
            "• **Clinical Action:** The lower leg has poor tissue elasticity. Defects > 2.0 cm typically require pedicled muscle flaps (Gastrocnemius/Soleus) or pedicled perforator flaps. Consult Plastic Surgery."
        )
    elif bed in unsafe_beds:
        st.error(
            "🔴 MANDATORY CONSULT REQUIRED (RED FLAG)\n\n"
            f"• **Reason:** Wound bed contains {bed}.\n"
            "• **Clinical Action:** Avascular beds will not nourish random local skin flaps. "
            "Risk of osteomyelitis, tendon necrosis, and breakdown. Consult Plastic Surgery for axial/muscle flap coverage."
        )
    elif max_dim > 4.0:
        st.error(
            "🔴 MANDATORY CONSULT REQUIRED (RED FLAG)\n\n"
            f"• **Reason:** Maximum dimension ({max_dim} cm) exceeds the 4.0 cm absolute limit for non-specialist local flap closure.\n"
            "• **Clinical Action:** Extreme closure tension risks flap ischemia and donor-site breakdown. Consult Plastic Surgery."
        )
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.step = 1
        with col2:
            if st.button("Next: Laxity & Geometry →"):
                st.session_state.width = width
                st.session_state.length = length
                st.session_state.bed = bed
                st.session_state.step = 3

# ------------------------------------------------------------------
# SCREEN 3: Laxity Vector & Geometry
# ------------------------------------------------------------------
elif st.session_state.step == 3:
    st.header("Step 3: Biomechanics & Laxity")

    shape = st.radio(
        "Defect Shape",
        ["Triangle / Wedge", "Circle / Ellipse", "Square / Rhombus / Rectangle"],
    )

    laxity = st.radio(
        "Primary Pinch Laxity Vector (Where is excess skin available?)",
        [
            "Axis A (Longitudinal): Parallel to long axis of limb",
            "Axis B (Lateral / Transverse): Perpendicular to defect / along limb circumference",
            "Axis C (Multi-Directional): Equal laxity in all directions",
            "Zero / Poor Laxity in All Axes (Rigid / Tight Skin)",
        ],
    )

    if laxity == "Zero / Poor Laxity in All Axes (Rigid / Tight Skin)":
        st.error(
            "🔴 MANDATORY CONSULT REQUIRED (RED FLAG)\n\n"
            "• **Reason:** Insufficient local tissue laxity.\n"
            "• **Clinical Action:** Local flap movement will cause excessive tension, leading to distal flap necrosis. Consult Plastic Surgery for regional flap or skin graft options."
        )
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.step = 2
        with col2:
            if st.button("Generate Ranked Surgical Options →"):
                st.session_state.shape = shape
                st.session_state.laxity = laxity
                st.session_state.selected_flap_idx = 0
                st.session_state.step = 4

# ------------------------------------------------------------------
# SCREEN 4: Ranked Surgical Options & Step-by-Step Execution
# ------------------------------------------------------------------
elif st.session_state.step == 4:
    st.header("Step 4: Operative Plan & Flap Execution")

    st.success("✅ STATUS: SAFE FOR LOCAL RECONSTRUCTION SUPPORT")

    w = st.session_state.width
    l = st.session_state.length
    shape = st.session_state.shape
    laxity = st.session_state.laxity
    subzone = st.session_state.subzone
    indication = st.session_state.indication

    def get_z_plasty():
        arm_length = l
        gain = round(l * 0.55, 1)  # Adjusted realistic intraoperative length gain (~55%)
        return {
            "name": "Z-Plasty (60° Transposition Flap)",
            "type": "Transposition",
            "measurements": f"• **Central Limb:** {l} cm (along scar vector)\n• **Side Arm Lengths:** {arm_length} cm at 60° angles\n• **Expected Clinical Gain:** ~{gain} cm (~50–60% functional gain)",
            "steps": [
                f"**Step 1 (Incision):** Incise the central limb along the scar line for {l} cm to release contracture.",
                f"**Step 2 (Arm Marking):** Draw two side arms of length {arm_length} cm at exact 60° angles from the central line.",
                "**Step 3 (Elevation):** Incise side arms down into subcutaneous fat; elevate two triangular flaps.",
                "**Step 4 (Transposition):** Swap the two triangular flaps across each other to rotate scar tension by 90°.",
                "**Step 5 (Closure):** Secure transposed flaps with subdermal 4-0 Vicryl and skin sutures under low tension."
            ]
        }

    def get_keystone():
        arc_width = round(w * 1.5, 1)  # Adjusted to 1.5x for safer extremity closure
        total_length = round(l * 3, 1)
        return {
            "name": "Keystone Perforator Island Flap (KPIF - Type I)",
            "type": "Fasciocutaneous Advancement",
            "measurements": f"• **Flap Arc Height:** {arc_width} cm (1.5:1 ratio relative to defect width {w} cm)\n• **Outer Curvilinear Length:** ~{total_length} cm\n• **Incision Angles:** 90° outward from defect ends",
            "steps": [
                f"**Step 1 (Design):** Expose defect as an ellipse. Draw a curvilinear arc adjacent to defect with max width = {arc_width} cm.",
                "**Step 2 (Outer Incision):** Cut outer curvilinear border down through deep fascia. **CRITICAL:** Do NOT undermine the flap bed to protect musculocutaneous perforators.",
                "**Step 3 (Fascial Release):** Incise deep fascia along the outer boundary to allow the keystone island to advance freely into the defect.",
                "**Step 4 (Closure):** Suture island into defect. Close outer corners in a V-Y configuration."
            ]
        }

    def get_vy():
        height = round(w * 3, 1)
        return {
            "name": "V-Y Advancement Flap",
            "type": "Linear Advancement",
            "measurements": f"• **Triangular Height:** {height} cm (3x defect base width of {w} cm)\n• **Pedicle Base:** Central subcutaneous blood supply centered beneath triangle",
            "steps": [
                f"**Step 1 (Design):** Mark a triangle with base = {w} cm at defect edge and height = {height} cm along laxity vector.",
                "**Step 2 (Incision):** Cut both lateral arms through dermis into subcutaneous tissue.",
                "**Step 3 (Mobilization):** Release peripheral dermal attachments while preserving deep central subcutaneous blood supply.",
                "**Step 4 (Advancement):** Slide triangle forward into defect gap. Suture donor tail linearly (V to Y)."
            ]
        }

    def get_rhomboid():
        side = max(w, l)
        return {
            "name": "Rhomboid (Limberg) Transposition Flap",
            "type": "Transposition",
            "measurements": f"• **Rhombus Side Length:** {side} cm (60° / 120° internal angles)\n• **Short Diagonal Extension:** {side} cm\n• **Transposition Arm:** {side} cm parallel to adjacent defect side",
            "steps": [
                f"**Step 1 (Preparation):** Excise defect into a standard 60°/120° rhombus with side length = {side} cm.",
                f"**Step 2 (Design):** Extend short diagonal outward by {side} cm. Draw a side arm ({side} cm) parallel to rhombus edge.",
                "**Step 3 (Elevation):** Incise flap down to deep fascia and elevate flap off tissue bed.",
                "**Step 4 (Transposition):** Transpose flap into main defect and close donor site primarily under low tension."
            ]
        }

    def get_rotation():
        radius = round(w * 2, 1)
        arc_length = round(w * 4.5, 1)
        return {
            "name": "Local Rotation Flap",
            "type": "Curvilinear Pivot",
            "measurements": f"• **Defect Base:** {w} cm\n• **Rotation Arc Length:** {arc_length} cm (4.5x defect width)\n• **Pivot Radius:** {radius} cm",
            "steps": [
                f"**Step 1 (Design):** Draw a curvilinear arc from defect edge sweeping {arc_length} cm along natural skin lines.",
                "**Step 2 (Incision):** Cut skin and subcutaneous fat along the arc line.",
                "**Step 3 (Undermining):** Undermine subcutaneous plane widely to enable smooth rotation.",
                "**Step 4 (Rotation):** Pivot flap into defect; place key tension-bearing suture at pivot point."
            ]
        }

    # Flap Selection Logic
    if "Linear Scar Contracture" in indication:
        options = [get_z_plasty(), get_rotation(), get_vy()]
    elif shape == "Triangle / Wedge" and "Axis A" in laxity:
        options = [get_vy(), get_rhomboid(), get_rotation()]
    elif subzone in ["Anterior Thigh", "Posterior Thigh", "Buttock / Gluteal Region", "Proximal / Mid Calf", "Forearm"] and 2.0 <= max(w, l) <= 4.0:
        options = [get_keystone(), get_rhomboid(), get_rotation()]
    else:
        options = [get_rotation(), get_rhomboid(), get_vy()]

    st.markdown("### 📋 Ranked Surgical Local Flap Options")
    st.info("Compare recommended options. Select a flap below to view incision metrics and surgical steps:")

    rank_labels = [f"Rank {i+1}: {opt['name']}" for i, opt in enumerate(options)]
    
    selected_rank = st.radio(
        "Select Flap Design to View Plan:",
        rank_labels,
        index=st.session_state.selected_flap_idx
    )
    
    active_idx = rank_labels.index(selected_rank)
    active_flap = options[active_idx]

    st.markdown("---")
    st.subheader(f"Option Details: {active_flap['name']}")
    st.caption(f"Movement Category: {active_flap['type']}")

    st.markdown("### 📐 Geometrical Dimensions & Incision Measurements")
    st.markdown(active_flap["measurements"])

    st.markdown("### 🔪 Step-by-Step Operative Protocol")
    for step in active_flap["steps"]:
        st.markdown(step)

    st.markdown("---")
    st.warning(
        "⚠️ **Surgical Safety & Perfusion Checklist:**\n"
        "1. Ensure donor closure lines run parallel to Relaxed Skin Tension Lines (RSTLs).\n"
        "2. **Perfusion Check:** Check capillary refill at flap edges. Pale skin indicates arterial insufficiency; dark purple/rapid refill indicates venous congestion.\n"
        "3. **Tension Release:** If flap tip blanches after suture placement, remove the distal suture immediately to prevent flap necrosis."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Laxity"):
            st.session_state.step = 3
    with col2:
        if st.button("🔄 New Patient Evaluation"):
            st.session_state.step = 1