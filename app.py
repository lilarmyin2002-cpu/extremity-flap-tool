import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Extremity & Trunk Local Flap Decision Tool", layout="centered"
)

# Initialize Session State
if "step" not in st.session_state:
    st.session_state.step = 1
if "selected_flap_idx" not in st.session_state:
    st.session_state.selected_flap_idx = 0

st.title("Extremity & Trunk Soft Tissue Decision Tool")
st.caption(
    "Clinical Decision Support for Non-Plastic Surgeons (Rule-Based Triage)"
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
    stasis = st.checkbox("Severe Stasis Dermatitis / Severe Edema / Peripheral Vascular Disease")

    red_flag_zones = [
        "Hand / Digits (High Complexity Zone)",
        "Distal Leg / Ankle / Foot (High Complexity Zone)",
    ]

    if subzone in red_flag_zones or radiation or stasis:
        st.error(
            "🔴 MANDATORY CONSULT REQUIRED (RED FLAG)\n\n"
            "• **Reason:** High-complexity subzone (Hand/Digits or Distal Leg) or severely compromised tissue bed.\n"
            "• **Clinical Action:** Do NOT attempt local flaps. High risk of flap failure, neurovascular injury, or joint contracture. Refer immediately to Plastic / Hand Surgery."
        )
    elif subzone in ["Elbow Joint Line (High Tension / Flexion Crease)", "Knee Joint Line (High Tension / Flexion Crease)"]:
        st.warning(
            "⚠️ HIGH-TENSION JOINT CREASE ZONE\n\n"
            "Wounds crossing flexion lines carry a high risk of dehiscence and disabling contractures. "
            "Reconstruction must incorporate strain-relieving designs (e.g., Z-Plasty or robust advancement)."
        )
        if st.button("Proceed with Caution to Defect Metrics →"):
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

    # Hard Stops for Size (> 4.0 cm) and Avascular Beds
    if bed in unsafe_beds:
        st.error(
            "🔴 MANDATORY CONSULT REQUIRED (RED FLAG)\n\n"
            f"• **Reason:** Wound bed contains {bed}.\n"
            "• **Clinical Action:** Avascular wound beds cannot support random local flaps. "
            "Risk of osteomyelitis, tendon necrosis, or total flap loss. Consult Plastic Surgery for regional/muscle flap coverage."
        )
    elif max_dim > 4.0:
        st.error(
            "🔴 MANDATORY CONSULT REQUIRED (RED FLAG)\n\n"
            f"• **Reason:** Maximum defect dimension ({max_dim} cm) exceeds the 4.0 cm safety threshold for non-specialist local flaps.\n"
            "• **Clinical Action:** Local random flaps on extremities > 4.0 cm carry extreme closure tension and high ischemic failure rates. Consult Plastic Surgery."
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
            "• **Reason:** Insufficient tissue laxity across all movement vectors.\n"
            "• **Clinical Action:** Local tissue rearrangement is geometrically impossible without severe tension, leading to flap necrosis and wound breakdown. Consult Plastic Surgery."
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

    st.success("✅ STATUS: SAFE FOR LOCAL RECONSTRUCTION")

    w = st.session_state.width
    l = st.session_state.length
    shape = st.session_state.shape
    laxity = st.session_state.laxity
    subzone = st.session_state.subzone
    indication = st.session_state.indication

    # Flap Generator Functions
    def get_z_plasty():
        arm_length = l
        gain = round(l * 0.75, 1)
        return {
            "name": "Z-Plasty (60° Transposition Flap)",
            "type": "Transposition",
            "measurements": f"• **Central Limb Length:** {l} cm (along scar)\n• **Side Arm Lengths:** {arm_length} cm at 60° angles\n• **Expected Longitudinal Gain:** ~{gain} cm (+75%)",
            "steps": [
                f"**Step 1 (Incision):** Incise the central limb along the scar line for {l} cm to release contracture.",
                f"**Step 2 (Arm Marking):** Draw two side arms of length {arm_length} cm at 60° angles from the ends of the central line, forming a 'Z'.",
                "**Step 3 (Elevation):** Incise the side arms down through subcutaneous fat and elevate two triangular flaps.",
                "**Step 4 (Transposition):** Interchangingly swap/transpose the two triangular flaps across each other to rotate tension 90°.",
                "**Step 5 (Closure):** Suture transposed flaps under resting tension using 4-0 or 5-0 monofilament."
            ]
        }

    def get_keystone():
        arc_width = w
        total_length = round(l * 3, 1)
        return {
            "name": "Keystone Perforator Island Flap (KPIF - Type I)",
            "type": "Fasciocutaneous Advancement",
            "measurements": f"• **Flap Arc Height:** {arc_width} cm (1:1 ratio with defect width)\n• **Outer Curvilinear Length:** ~{total_length} cm\n• **Incision Angle:** 90° outward from defect ends",
            "steps": [
                f"**Step 1 (Design):** Prepare defect as an ellipse. Draw a curvilinear arc adjacent to the defect with width = {arc_width} cm.",
                "**Step 2 (Incision):** Incise outer skin border through deep fascia. **DO NOT** undermine the underside of the flap to preserve perforators.",
                "**Step 3 (Advancement):** Mobilize outer margins bluntly to advance the keystone island laterally into the wound.",
                "**Step 4 (Closure):** Suture island into defect. Close outer ends in a V-Y configuration."
            ]
        }

    def get_vy():
        height = round(w * 3, 1)
        return {
            "name": "V-Y Advancement Flap",
            "type": "Linear Advancement",
            "measurements": f"• **Triangular Height:** {height} cm (3x defect base width of {w} cm)\n• **Pedicle Base:** Central subcutaneous blood supply centered beneath triangle",
            "steps": [
                f"**Step 1 (Design):** Mark a triangle with its base at the defect edge and height = {height} cm aligned with laxity.",
                "**Step 2 (Incision):** Cut both lateral arms through dermis into subcutaneous tissue.",
                "**Step 3 (Mobilization):** Release peripheral attachments while preserving deep central subcutaneous blood supply.",
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
                f"**Step 1 (Preparation):** Convert defect into a 60°/120° rhombus with side lengths of {side} cm.",
                f"**Step 2 (Design):** Extend short diagonal outward by {side} cm. Draw a second line ({side} cm) parallel to rhombus edge.",
                "**Step 3 (Elevation):** Incise flap down to deep fascia.",
                "**Step 4 (Transposition):** Step/pivot flap laterally into main defect and close donor site primarily."
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

    def get_h_plasty():
        arm_len = round(l * 1.5, 1)
        return {
            "name": "Bipedicle Advancement Flap (H-Plasty)",
            "type": "Bilateral Advancement",
            "measurements": f"• **Defect Width:** {w} cm\n• **Parallel Incision Arms (x4):** {arm_len} cm extending from defect corners\n• **Total Flap Advancement:** ~{round(w/2, 1)} cm from each side",
            "steps": [
                f"**Step 1 (Design):** For a square/rectangular defect, draw 4 parallel relief incisions ({arm_len} cm each) extending from the 4 corners.",
                "**Step 2 (Incision & Undermining):** Incise lines down to fascia and undermine both opposing rectangular flaps extensively.",
                "**Step 3 (Advancement):** Advance both flaps inward toward each other to meet in the middle over the wound bed.",
                "**Step 4 (Closure):** Suture central meeting line and close side incision arms in an 'H' configuration."
            ]
        }

    # ------------------------------------------------------------------
    # RANKING ALGORITHM (PRIMARY, SECONDARY, TERTIARY)
    # ------------------------------------------------------------------
    options = []

    if "Linear Scar Contracture" in indication:
        options = [get_z_plasty(), get_rotation(), get_vy()]
    elif shape == "Triangle / Wedge" and "Axis A" in laxity:
        options = [get_vy(), get_rhomboid(), get_rotation()]
    elif shape == "Square / Rhombus / Rectangle" and "Axis B" in laxity:
        options = [get_rhomboid(), get_h_plasty(), get_rotation()]
    elif subzone in ["Anterior Thigh", "Posterior Thigh", "Buttock / Gluteal Region", "Proximal / Mid Calf", "Forearm"] and 2.5 <= max(w, l) <= 4.0:
        options = [get_keystone(), get_rhomboid(), get_rotation()]
    elif shape == "Square / Rhombus / Rectangle":
        options = [get_h_plasty(), get_rhomboid(), get_vy()]
    else:
        options = [get_rotation(), get_rhomboid(), get_vy()]

    # Display Options Selector
    st.markdown("### 📋 Ranked Surgical Local Flap Options")
    st.info("Plastic surgery principles favor comparing multiple local flap designs for a given defect. Select an option below to view its specific geometrical plan and operative steps:")

    rank_labels = [f"Rank {i+1}: {opt['name']}" for i, opt in enumerate(options)]
    
    selected_rank = st.radio(
        "Select Flap Design to View Plan:",
        rank_labels,
        index=st.session_state.selected_flap_idx
    )
    
    active_idx = rank_labels.index(selected_rank)
    active_flap = options[active_idx]

    # Render Active Flap Details
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
        "⚠️ **Surgical Safety Checklist:**\n"
        "1. Ensure donor closure lines run parallel to Relaxed Skin Tension Lines (RSTLs).\n"
        "2. Avoid crossing flexure lines perpendicularly without a strain-relieving Z-plasty modification.\n"
        "3. Always check capillary refill at flap margins after placing key tension-bearing sutures."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Laxity"):
            st.session_state.step = 3
    with col2:
        if st.button("🔄 New Patient Evaluation"):
            st.session_state.step = 1
