import glob
import math
import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(
    page_title="Extremity & Trunk Local Flap Decision Tool", layout="centered"
)

if "step" not in st.session_state:
    st.session_state.step = 1
if "selected_flap_idx" not in st.session_state:
    st.session_state.selected_flap_idx = 0

st.title("Extremity & Trunk Soft Tissue Decision Tool")
st.caption("Clinical Decision Support & Risk Triage for Non-Plastic Surgeons")

# Helper function to find images dynamically regardless of extension
def resolve_image_path(base_filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, "assets", "flap_picture")
    
    # Try exact match first
    exact_path = os.path.join(target_dir, base_filename)
    if os.path.exists(exact_path) and os.path.isfile(exact_path):
        return exact_path

    # Search for files starting with base_filename (handles .png, .jpg, no-extension, etc.)
    pattern = os.path.join(target_dir, f"{base_filename}*")
    matches = glob.glob(pattern)
    
    for match in matches:
        if os.path.isfile(match):
            return match
            
    return None


LABEL_COLOR = (11, 61, 145, 255)


def line_label(text, p1, p2, offset=0, away_from=None, size=13):
    """Label whose baseline runs parallel to the line p1-p2.

    The label is centred on the line's midpoint and pushed `offset` pixels
    perpendicular to it, on the side facing away from `away_from`.
    """
    (x1, y1), (x2, y2) = p1, p2
    if x2 < x1 or (x2 == x1 and y2 > y1):  # keep text reading left-to-right / upward
        x1, y1, x2, y2 = x2, y2, x1, y1
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    nx, ny = -dy / length, dx / length
    if away_from is not None and (mx - away_from[0]) * nx + (my - away_from[1]) * ny < 0:
        nx, ny = -nx, -ny
    return {
        "text": text,
        "x": mx + nx * offset,
        "y": my + ny * offset,
        "angle": -math.degrees(math.atan2(dy, dx)),  # PIL rotates counter-clockwise
        "size": size,
    }


def annotate_image(image_path, labels):
    """Write measurement labels onto a flap diagram.

    labels: list of {"text", "x", "y", "angle", "size"} in pixel coordinates
    of the source image (see line_label). The original file is never modified.
    """
    img = Image.open(image_path).convert("RGBA")
    if not labels:
        return img

    # Draw 4x larger and downsample so the text is anti-aliased
    scale = 4
    big = img.resize((img.width * scale, img.height * scale), Image.LANCZOS)

    def load_font(size):
        for font_path, index in (
            ("/System/Library/Fonts/Helvetica.ttc", 1),
            ("/Library/Fonts/Arial Bold.ttf", 0),
            ("DejaVuSans-Bold.ttf", 0),
        ):
            try:
                return ImageFont.truetype(font_path, size, index=index)
            except OSError:
                continue
        return ImageFont.load_default(size=size)

    for label in labels:
        font = load_font(int(label["size"] * scale))
        left, top, right, bottom = font.getbbox(label["text"])
        pad = 4 * scale
        tile = Image.new("RGBA", (right - left + 2 * pad, bottom - top + 2 * pad), (0, 0, 0, 0))
        ImageDraw.Draw(tile).text((pad - left, pad - top), label["text"], fill=LABEL_COLOR, font=font)
        tile = tile.rotate(label["angle"], expand=True, resample=Image.BICUBIC)
        big.alpha_composite(
            tile,
            (
                int(label["x"] * scale - tile.width / 2),
                int(label["y"] * scale - tile.height / 2),
            ),
        )

    return big.resize(img.size, Image.LANCZOS).convert("RGB")


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
    elif subzone in [
        "Elbow Joint Line (High Tension / Flexion Crease)",
        "Knee Joint Line (High Tension / Flexion Crease)",
    ]:
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

    width = st.number_input(
        "Defect Width (cm)", min_value=0.5, max_value=15.0, value=2.5, step=0.5
    )
    length = st.number_input(
        "Defect Length / Scar Length (cm)",
        min_value=0.5,
        max_value=20.0,
        value=3.0,
        step=0.5,
    )

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
        gain = round(l * 0.55, 1)
        return {
            "name": "Z-Plasty (60° Transposition Flap)",
            "type": "Transposition",
            "image_key": "z-plasty final",
            "labels": [
                line_label(f"{l} cm", (228, 283), (228, 65), offset=14, away_from=(300, 175)),
                line_label(f"{l} cm", (493, 280), (493, 62), offset=22, away_from=(520, 170)),
                line_label(f"{arm_length} cm", (392, 161), (493, 62), offset=11, away_from=(500, 150)),
                line_label(f"{arm_length} cm", (492, 280), (587, 173), offset=11, away_from=(490, 200)),
            ],
            "measurements": f"• **Central Limb:** {l} cm (along scar vector)\n• **Side Arm Lengths:** {arm_length} cm at 60° angles\n• **Expected Clinical Gain:** ~{gain} cm (~50–60% functional gain)",
            "steps": [
                f"**Step 1 (Incision):** Incise the central limb along the scar line for {l} cm to release contracture.",
                f"**Step 2 (Arm Marking):** Draw two side arms of length {arm_length} cm at exact 60° angles from the central line.",
                "**Step 3 (Elevation):** Incise side arms down into subcutaneous fat; elevate two triangular flaps.",
                "**Step 4 (Transposition):** Swap the two triangular flaps across each other to rotate scar tension by 90°.",
                "**Step 5 (Closure):** Secure transposed flaps with subdermal 4-0 Vicryl and skin sutures under low tension.",
            ],
        }

    def get_keystone():
        arc_width = round(w * 1.5, 1)
        tip_line = arc_width  # 90° line at each defect tip is drawn as long as the flap arc height
        total_length = round(l * 3, 1)
        return {
            "name": "Keystone Perforator Island Flap (KPIF - Type I)",
            "type": "Fasciocutaneous Advancement",
            "image_key": "keystone final",
            "labels": [
                {"text": f"{w} cm", "x": 252, "y": 277, "angle": 0, "size": 12},
                {"text": f"{arc_width} cm", "x": 320, "y": 277, "angle": 0, "size": 12},
                line_label(f"{tip_line} cm", (257, 200), (304, 162), offset=11, away_from=(300, 250), size=11),
                line_label(f"{tip_line} cm", (258, 362), (298, 403), offset=11, away_from=(300, 300), size=11),
            ],
            "measurements": f"• **Flap Arc Height:** {arc_width} cm (1.5:1 ratio relative to defect width {w} cm)\n• **90° Line at Each Defect Tip:** {tip_line} cm (drawn at a right angle to the long axis of the defect)\n• **Outer Curvilinear Length:** ~{total_length} cm",
            "steps": [
                f"**Step 1 (Mark the flap):** Shape the wound into an oval. From each pointed end (tip) of the oval, draw a straight line going out at a right angle (90°) to the long axis of the wound, {tip_line} cm long. At the middle of the wound, measure {arc_width} cm straight out from the wound edge and make a dot. Join the ends of the two lines with a smooth curve that passes through the dot. This curved shape is the flap.",
                "**Step 2 (Cut the flap):** Cut along the two straight lines and the curve you drew, through the skin and fat down to the deep fascia (the tough layer over the muscle). **CRITICAL:** Do NOT lift or undermine the tissue under the flap. This protects the small blood vessels (perforators) that feed it.",
                "**Step 3 (Free the flap):** Along the curved outer edge, cut through the deep fascia as well, so the flap is loose enough to slide sideways into the wound.",
                "**Step 4 (Closure):** Suture island into defect. Close outer corners in a V-Y configuration.",
            ],
        }

    def get_vy():
        height = round(w * 3, 1)
        return {
            "name": "V-Y Advancement Flap",
            "type": "Linear Advancement",
            "image_key": "vy final",
            "labels": [
                {"text": f"{w} cm", "x": 80.5, "y": 235, "angle": 0, "size": 13},
                {"text": f"{height} cm", "x": 88, "y": 348, "angle": -90, "size": 13},
            ],
            "measurements": f"• **Triangular Height:** {height} cm (3x defect base width of {w} cm)\n• **Pedicle Base:** Central subcutaneous blood supply centered beneath triangle",
            "steps": [
                f"**Step 1 (Design):** Mark a triangle with base = {w} cm at defect edge and height = {height} cm along laxity vector.",
                "**Step 2 (Incision):** Cut both lateral arms through dermis into subcutaneous tissue.",
                "**Step 3 (Mobilization):** Release peripheral dermal attachments while preserving deep central subcutaneous blood supply.",
                "**Step 4 (Advancement):** Slide triangle forward into defect gap. Suture donor tail linearly (V to Y).",
            ],
        }

    def get_rhomboid():
        side = max(w, l)
        return {
            "name": "Rhomboid (Limberg) Transposition Flap",
            "type": "Transposition",
            "image_key": "rhomboid final",
            "labels": [
                line_label(f"{side} cm", a, b, offset=off, away_from=(188, 153), size=11)
                for a, b, off in (
                    ((188, 74), (143, 153), 15),   # AB
                    ((188, 74), (234, 153), 10),   # AD
                    ((143, 153), (188, 232), 15),  # BC
                    ((234, 153), (188, 232), 10),  # DC
                )
            ]
            + [
                line_label(f"{side} cm", (234, 153), (310, 154), offset=10, away_from=(272, 200), size=11),  # DE
                line_label(f"{side} cm", (310, 154), (267, 228), offset=12, away_from=(250, 170), size=11),  # EF
            ],
            "measurements": f"• **Rhombus Side Length:** {side} cm (60° / 120° internal angles)\n• **Short Diagonal Extension:** {side} cm\n• **Transposition Arm:** {side} cm parallel to adjacent defect side",
            "steps": [
                f"**Step 1 (Preparation):** Excise defect into a standard 60°/120° rhombus with side length = {side} cm.",
                f"**Step 2 (Design):** Extend short diagonal outward by {side} cm. Draw a side arm ({side} cm) parallel to rhombus edge.",
                "**Step 3 (Elevation):** Incise flap down to deep fascia and elevate flap off tissue bed.",
                "**Step 4 (Transposition):** Transpose flap into main defect and close donor site primarily under low tension.",
            ],
        }

    def get_rotation():
        arc_radius = max(w, l)
        arc_length = round(arc_radius * 4, 1)
        return {
            "name": "Standard Rotation Flap",
            "type": "Pivotal Rotation",
            "image_key": "rotation final",
            "measurements": f"• **Curvilinear Arc Length:** ~{arc_length} cm (4x defect diameter)\n• **Base Width:** Must equal or exceed defect width ({w} cm)",
            "steps": [
                f"**Step 1 (Triangulation):** Convert defect into a triangular geometry.",
                f"**Step 2 (Arc Marking):** Draw a semicircular arc extending from defect base, ~{arc_length} cm long.",
                "**Step 3 (Elevation):** Incise along arc down through subcutaneous tissue; elevate flap while keeping pedicle intact.",
                "**Step 4 (Rotation & Closure):** Rotate flap into defect. Use back-cut only if tension prevents full alignment.",
            ],
        }

    # Flap Selection Logic
    if "Linear Scar Contracture" in indication:
        options = [get_z_plasty(), get_rotation(), get_vy()]
    elif shape == "Triangle / Wedge" and "Axis A" in laxity:
        options = [get_vy(), get_rhomboid(), get_rotation()]
    elif (
        subzone
        in [
            "Anterior Thigh",
            "Posterior Thigh",
            "Buttock / Gluteal Region",
            "Proximal / Mid Calf",
            "Forearm",
        ]
        and 2.0 <= max(w, l) <= 4.0
    ):
        options = [get_keystone(), get_rhomboid(), get_rotation()]
    else:
        options = [get_rotation(), get_rhomboid(), get_vy()]

    st.markdown("### 📋 Ranked Surgical Local Flap Options")
    st.info(
        "Compare recommended options. Select a flap below to view incision metrics and surgical steps:"
    )

    rank_labels = [f"Rank {i+1}: {opt['name']}" for i, opt in enumerate(options)]

    selected_rank = st.radio(
        "Select Flap Design to View Plan:",
        rank_labels,
        index=st.session_state.selected_flap_idx,
    )

    active_idx = rank_labels.index(selected_rank)
    active_flap = options[active_idx]

    st.markdown("---")
    st.subheader(f"Option Details: {active_flap['name']}")
    st.caption(f"Movement Category: {active_flap['type']}")

    # Dynamic File Resolution
    resolved_image_path = resolve_image_path(active_flap["image_key"])

    if resolved_image_path:
        st.image(
            annotate_image(resolved_image_path, active_flap.get("labels", [])),
            caption=f"Surgical Diagram: {active_flap['name']}",
            use_container_width=True,
        )
    else:
        st.error(
            f"⚠️ Image file starting with `{active_flap['image_key']}` was not found inside your `assets/flap_picture` directory."
        )

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
