import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Extremity Local Flap Clinical Decision Tool", layout="centered"
)

# Initialize Session State for Wizard Navigation
if "step" not in st.session_state:
    st.session_state.step = 1

st.title("Extremity & Trunk Soft Tissue Decision Tool")
st.caption(
    "Clinical Decision Support for Non-Plastic Surgeons (Rule-Based Triage)"
)

# ------------------------------------------------------------------
# SCREEN 1: Location & Safety Screening
# ------------------------------------------------------------------
if st.session_state.step == 1:
    st.header("Step 1: Location & Red Flags")

    subzone = st.selectbox(
        "Select Anatomical Subzone",
        [
            "Upper Arm",
            "Forearm",
            "Hand / Digits (High Complexity Zone)",
            "Anterior Thigh",
            "Posterior Thigh",
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

    # Hard Stop Red Flags
    red_flag_zones = [
        "Hand / Digits (High Complexity Zone)",
        "Distal Leg / Ankle / Foot (High Complexity Zone)",
    ]

    if subzone in red_flag_zones or radiation or stasis:
        st.error(
            "🔴 MANDATORY CONSULT REQUIRED (RED FLAG)\n\n"
            "• **Reason:** High-complexity zone (Hand/Digits or Distal Leg) or severely compromised tissue bed.\n"
            "• **Clinical Action:** Do NOT attempt random local flaps. High risk of flap failure, tendon/neurovascular injury, or disabling joint contracture. Refer immediately to Plastic / Hand Surgery."
        )
    else:
        if st.button("Next: Defect Metrics →"):
            st.session_state.subzone = subzone
            st.session_state.indication = indication
            st.session_state.step = 2

# ------------------------------------------------------------------
# SCREEN 2: Defect Metrics & Bed Quality
# ------------------------------------------------------------------
elif st.session_state.step == 2:
    st.header("Step 2: Defect Metrics & Bed Quality")

    width = st.number_input("Defect Width (cm)", min_value=0.5, max_value=15.0, value=2.5, step=0.5)
    length = st.number_input("Defect Length / Scar Length (cm)", min_value=0.5, max_value=20.0, value=3.0, step=0.5)

    bed = st.radio(
        "Deep Wound Bed Quality",
        [
            "Healthy Muscle / Intact Subcutaneous Tissue / Granulation",
            "Intact Periosteum or Peritenon",
            "Bare Bone (No Periosteum)",
            "Exposed Tendon (No Peritenon)",
            "Exposed Orthopedic / Vascular Hardware",
        ],
    )

    # Red Flag Validation for Bed & Size
    if st.session_state.subzone == "Proximal / Mid Calf" and bed in [
        "Bare Bone (No Periosteum)",
        "Exposed Tendon (No Peritenon)",
        "Exposed Orthopedic / Vascular Hardware",
    ]:
        st.error(
            "🔴 RED FLAG: Avascular / Complex Bed on Lower Extremity. Random local flaps will fail over bare bone/tendon/hardware. Consult Plastic Surgery for regional muscle/fasciocutaneous coverage."
        )
    elif max(width, length) > 6.0 and "Keystone" not in st.session_state.get("indication", ""):
        st.error(
            "🔴 RED FLAG: Defect exceeds 6.0 cm. Too large for standard random local flaps on limbs. Consider Skin Graft (if bed vascular) or Consult Plastic Surgery."
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
            "Axis B (Lateral / Transverse): Perpendicular (90°) to defect / along limb circumference",
            "Axis C (Multi-Directional): Equal laxity in all directions",
        ],
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.step = 2
    with col2:
        if st.button("Generate Surgical Plan →"):
            st.session_state.shape = shape
            st.session_state.laxity = laxity
            st.session_state.step = 4

# ------------------------------------------------------------------
# SCREEN 4: Surgical Plan & Step-by-Step Procedure
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

    # ------------------------------------------------------------------
    # DECISION ENGINE LOGIC
    # ------------------------------------------------------------------
    if "Linear Scar Contracture" in indication:
        flap_name = "Z-Plasty (60° Transposition Flap)"
        arm_length = l
        gain = round(l * 0.75, 1)

        measurements = f"• **Central Limb Length:** {l} cm (along scar)\n• **Side Arm Lengths:** {arm_length} cm at 60° angles\n• **Expected Longitudinal Gain:** ~{gain} cm (+75%)"
        
        steps = [
            f"**Step 1 (Incision):** Incise the central limb along the scar for {l} cm to release tension.",
            f"**Step 2 (Arm Marking):** At each end of the central line, draw a side arm of length {arm_length} cm at a 60° angle, forming a 'Z' shape.",
            "**Step 3 (Elevation):** Incise the side arms and elevate the two triangular skin flaps including full-thickness subcutaneous fat.",
            "**Step 4 (Transposition):** Transpose (swap) the two triangular flaps across each other. This rotates the original line of tension by 90°.",
            "**Step 5 (Closure):** Suture the transposed flaps in place using 4-0 or 5-0 monofilament sutures."
        ]

    elif subzone in ["Anterior Thigh", "Posterior Thigh", "Buttock / Gluteal Region", "Proximal / Mid Calf", "Forearm"] and 3.0 <= max(w, l) <= 6.0 and shape == "Circle / Ellipse":
        flap_name = "Keystone Perforator Island Flap (KPIF - Type I)"
        arc_width = w
        total_length = round(l * 3, 1)

        measurements = f"• **Flap Width (Arc Height):** {arc_width} cm (1:1 ratio with defect width)\n• **Outer Flap Curvilinear Length:** ~{total_length} cm\n• **Incision Margin:** Extends 90° from defect ends."

        steps = [
            f"**Step 1 (Design):** Excise defect as an ellipse parallel to the limb long axis. Draw a curvilinear keystone arc adjacent to defect with width = {arc_width} cm.",
            f"**Step 2 (Incision):** Incise the outer skin border through deep fascia. **CRITICAL:** Do NOT undermine the deep surface of the flap—preserve underlying muscle/fascial perforators.",
            f"**Step 3 (Advancement):** Bluntly mobilize the outer margin to allow the keystone island to advance laterally into the defect.",
            "**Step 4 (Closure):** Suture the central flap into the defect. Close the two outer ends in a V-Y fashion to relieve tension."
        ]

    elif shape == "Triangle / Wedge" and "Axis A" in laxity:
        flap_name = "V-Y Advancement Flap"
        height = round(w * 3, 1)

        measurements = f"• **Triangular Flap Height:** {height} cm (3x defect base width of {w} cm)\n• **Pedicle Base:** Centered directly under the triangular skin island."

        steps = [
            f"**Step 1 (Design):** Draw a triangle extending from the defect base with a height of {height} cm in the direction of skin laxity.",
            "**Step 2 (Incision):** Incise both lateral arms of the triangle through skin and superficial fat.",
            "**Step 3 (Mobilization):** Release fibrous attachments at the margins while keeping the deep central subcutaneous pedicle completely intact for blood supply.",
            f"**Step 4 (Advancement & Closure):** Advance the triangle linearly forward into the defect gap. Suture the donor tail straight, converting the 'V' incision into a 'Y'."
        ]

    elif "Axis B" in laxity or shape == "Square / Rhombus / Rectangle":
        flap_name = "Rhomboid (Limberg) Transposition Flap"
        side = max(w, l)
        short_diag = side

        measurements = f"• **Defect Rhombus Sides:** {side} cm at 60° / 120° angles\n• **Flap Extension Line:** {side} cm extending straight from short diagonal\n• **Flap Transposition Arm:** {side} cm parallel to adjacent defect side"

        steps = [
            f"**Step 1 (Preparation):** Convert defect into a 60°/120° rhombus with side lengths of {side} cm.",
            f"**Step 2 (Design):** Extend the short diagonal line outward by {side} cm. From that point, draw a second line of {side} cm parallel to the rhombus edge.",
            "**Step 3 (Elevation):** Incise flap through skin and subcutaneous fat down to deep fascia.",
            "**Step 4 (Transposition):** Pivot/step the flap laterally into the main defect. Close donor site primarily."
        ]

    else:
        flap_name = "Local Rotation Flap"
        radius = round(w * 2, 1)
        arc_length = round(w * 4.5, 1)

        measurements = f"• **Defect Base:** {w} cm\n• **Rotation Arc Length:** {arc_length} cm (4.5x defect width)\n• **Pivot Radius:** {radius} cm"

        steps = [
            f"**Step 1 (Design):** Draw a curvilinear arc extending from the defect edge, sweeping around {arc_length} cm along natural tension lines.",
            "**Step 2 (Incision):** Incise skin and subcutaneous tissue along the curved line.",
            "**Step 3 (Undermining):** Undermine the flap in the subcutaneous plane to allow smooth pivoting without skin puckering.",
            "**Step 4 (Rotation & Closure):** Rotate the flap into the defect. Suture under minimal tension. Add a small back-cut at the end if extra reach is required."
        ]

    # Display Results
    st.subheader(f"Recommended Procedure: {flap_name}")
    st.markdown("---")
    
    st.markdown("### 📐 Geometrical Dimensions & Incision Measurements")
    st.markdown(measurements)

    st.markdown("---")
    st.markdown("### 🔪 Step-by-Step Operative Protocol")
    for s in steps:
        st.markdown(s)

    st.markdown("---")
    st.warning(
        "⚠️ **Surgical Safety Checklist:**\n"
        "1. Ensure donor closure line runs parallel to relaxed skin tension lines (RSTLs).\n"
        "2. Avoid crossing flexure joints perpendicularly without a Z-plasty modification.\n"
        "3. Always verify capillary refill at the flap tips after placing key tension-bearing sutures."
    )

    if st.button("← Start Over / New Patient"):
        st.session_state.step = 1
