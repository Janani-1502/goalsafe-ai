import html
import io
from datetime import datetime

import streamlit as st
from PIL import Image

from hazard_verifier import assess_image


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="GoalSafe AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "current_page": "Home",
    "assessment_result": None,
    "assessment_image": None,
    "assessment_evidence": None,
    "assessment_guidance": None,
    "assessment_decision": None,
    "assessment_history": [],
    "assessment_reset": 0,
    "assessment_saved": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# HTML HELPER
# =========================================================

def render_html(content):
    st.html(content)


# =========================================================
# CUSTOM CSS
# =========================================================

render_html("""
<style>

/* =======================================================
   GLOBAL
   ======================================================= */

.stApp {
    background:
        radial-gradient(
            900px 500px at 15% -10%,
            rgba(124, 58, 237, 0.15),
            transparent 60%
        ),
        radial-gradient(
            800px 500px at 90% 0%,
            rgba(139, 92, 246, 0.10),
            transparent 55%
        ),
        #07060D;

    color: #F5F4F8;
}

.main .block-container {
    max-width: 1500px;

    padding-top: 8px !important;
    padding-bottom: 60px;

    padding-left: 15px !important;
    padding-right: 40px !important;
}

/* =======================================================
   SIDEBAR
   ======================================================= */

section[data-testid="stSidebar"] {
    background: #0A0913;
    border-right: 1px solid rgba(255,255,255,0.07);
}

section[data-testid="stSidebar"] > div {
    padding: 8px 22px !important;
}


/* Brand */

.brand {
    padding: 4px 14px 25px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 28px;
}

.brand-icon {
    font-size: 30px;
    margin-bottom: 12px;
}

.brand-name {
    font-size: 23px;
    font-weight: 800;
    color: #F5F4F8;
}

.brand-name span {
    color: #F5F4F8;
}

.brand-sub {
    margin-top: 5px;
    font-size: 12px;
    color: #A78BFA;
    font-weight: 600;
}


/* Sidebar section */

.side-label {
    margin: 20px 14px 9px;

    color: #A78BFA;
    font-size: 11px;
    font-weight: 700;

    letter-spacing: 1px;
    text-transform: uppercase;
}


/* Sidebar buttons */

section[data-testid="stSidebar"] .stButton {
    margin: 0 !important;
    padding: 0 !important;
}

section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    min-height: 48px !important;

    margin: 3px 0 !important;
    padding: 0 14px !important;

    border-radius: 10px !important;
    border: 1px solid transparent !important;

    font-size: 14px !important;
    font-weight: 500 !important;

    justify-content: flex-start !important;
    text-align: left !important;
}

section[data-testid="stSidebar"] .stButton > button > div {
    width: 100% !important;
    justify-content: flex-start !important;
}

section[data-testid="stSidebar"] .stButton > button p {
    width: 100% !important;
    text-align: left !important;
}


/* Inactive */

section[data-testid="stSidebar"]
button[data-testid="stBaseButton-secondary"] {
    background: transparent !important;
    color: #A3A0B5 !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"]
button[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(139, 92, 246, 0.08) !important;
    color: #FFFFFF !important;
}


/* Active */

section[data-testid="stSidebar"]
button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(
        135deg,
        #8B5CF6,
        #5B21B6
    ) !important;

    color: #FFFFFF !important;

    box-shadow:
        0 6px 20px rgba(124,58,237,0.30) !important;

    font-weight: 700 !important;
}


/* =======================================================
   HEADERS
   ======================================================= */

.greeting {
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #A855F7;
}

.greeting .name {
    color: #A855F7;
}
.header-subtitle {
    margin-top: 6px;
    color: #A3A0B5;
    font-size: 14px;
}


/* =======================================================
   HOME STAT CARDS
   ======================================================= */

.home-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 22px;

    margin-top: 34px;
    margin-bottom: 38px;
}

.stat-card {
    min-height: 140px;

    padding: 25px;

    background: rgba(18,17,32,0.78);

    border: 1px solid rgba(139,92,246,0.18);
    border-radius: 18px;
}

.stat-title {
    color: #A3A0B5;
    font-size: 14px;
}

.stat-number {
    margin-top: 10px;

    color: #A855F7;

    font-size: 36px;
    font-weight: 800;
}

.stat-number.red {
    color: #F87171;
}

.stat-number.green {
    color: #4ADE80;
}

.stat-sub {
    margin-top: 3px;
    color: #6F6C82;
    font-size: 12px;
}


/* =======================================================
   RECENT ASSESSMENTS
   ======================================================= */

.section-title {
    margin: 10px 0 16px;

    font-size: 21px;
    font-weight: 800;
}

.assessment-card {
    padding: 20px 22px;
    margin-bottom: 12px;

    background: rgba(10,9,19,0.70);

    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
}

.assessment-time {
    color: #77738A;
    font-size: 12px;
    margin-bottom: 9px;
}

.assessment-goal {
    color: #F5F4F8;
    font-size: 15px;
    font-weight: 700;
}

.assessment-status {
    margin-top: 10px;

    color: #A855F7;
    font-size: 13px;
    font-weight: 600;
}


/* =======================================================
   NEW ASSESSMENT STEPPER
   ======================================================= */

.stepper {
    display: flex;
    align-items: center;

    gap: 12px;

    padding: 18px 22px;
    margin: 28px 0 25px;

    background: rgba(18,17,32,0.78);

    border: 1px solid rgba(139,92,246,0.17);
    border-radius: 18px;
}

.step {
    display: flex;
    align-items: center;

    gap: 9px;

    color: #6F6C82;

    font-size: 14px;
    font-weight: 600;

    flex: 1;
}

.step.active {
    color: #F5F4F8;
}

.step-number {
    width: 34px;
    height: 34px;
    min-width: 34px;

    border-radius: 50%;

    border: 1px solid #6F6C82;

    display: flex;
    align-items: center;
    justify-content: center;
}

.step.active .step-number {
    border: none;

    background: linear-gradient(
        135deg,
        #A855F7,
        #6D28D9
    );

    color: white;
}

.step-arrow {
    color: #A855F7;
    font-size: 20px;
}


/* =======================================================
   INPUT CARDS
   ======================================================= */

.input-card {
    min-height: 115px;

    padding: 22px;

    background: rgba(18,17,32,0.78);

    border: 1px solid rgba(139,92,246,0.18);
    border-radius: 18px;

    margin-bottom: 14px;
}

.input-title {
    font-size: 18px;
    font-weight: 700;
}

.input-description {
    margin-top: 7px;

    color: #77738A;
    font-size: 13px;
    line-height: 1.5;
}


/* =======================================================
   FILE UPLOADER
   ======================================================= */

[data-testid="stFileUploader"] {
    border: 1.5px dashed rgba(139,92,246,0.45);

    border-radius: 13px;

    background: rgba(7,6,13,0.55);

    padding: 12px;
}

[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
}


/* =======================================================
   TEXT AREA
   ======================================================= */

textarea {
    background: #0B0A14 !important;

    color: #F5F4F8 !important;

    border: 1px solid rgba(139,92,246,0.25) !important;

    border-radius: 12px !important;
}

textarea:focus {
    border-color: #8B5CF6 !important;

    box-shadow:
        0 0 0 1px #8B5CF6 !important;
}


/* =======================================================
   ASSESS BUTTON
   ======================================================= */

.assess-button-container {
    margin-top: 12px;
}


/* All normal main buttons */

.main .stButton > button {
    border-radius: 11px !important;

    font-weight: 700 !important;
}


/* Assess button */

.assess-button-container + div .stButton > button,
button[kind="primary"] {
    background: linear-gradient(
        135deg,
        #8B5CF6,
        #5B21B6
    ) !important;

    color: white !important;

    border: none !important;

    box-shadow:
        0 7px 20px rgba(124,58,237,0.30) !important;
}

button[kind="primary"]:hover {
    background: linear-gradient(
        135deg,
        #A855F7,
        #6D28D9
    ) !important;
}


/* =======================================================
   RESULT
   ======================================================= */

.result-title {
    margin: 30px 0 15px;

    font-size: 21px;
    font-weight: 800;
}

.result-banner {
    display: flex;
    align-items: center;

    gap: 18px;

    padding: 20px;

    margin-bottom: 20px;

    border: 1px solid rgba(139,92,246,0.35);
    border-radius: 15px;

    background:
        linear-gradient(
            135deg,
            rgba(124,58,237,0.15),
            rgba(18,17,32,0.65)
        );
}

.result-icon {
    width: 56px;
    height: 56px;
    min-width: 56px;

    border-radius: 50%;

    display: flex;
    align-items: center;
    justify-content: center;

    background: rgba(124,58,237,0.18);

    border: 1px solid #8B5CF6;

    font-size: 27px;
}

.result-heading {
    color: #A855F7;

    font-size: 21px;
    font-weight: 800;
}

.result-description {
    margin-top: 6px;

    color: #F5F4F8;

    font-size: 14px;
    line-height: 1.55;
}

.result-card {
    min-height: 190px;

    padding: 20px;

    background: rgba(10,9,19,0.65);

    border: 1px solid rgba(255,255,255,0.07);

    border-radius: 14px;
}

.result-card-title {
    margin-bottom: 14px;

    color: #F5F4F8;

    font-size: 16px;
    font-weight: 700;
}

.result-text {
    color: #A3A0B5;

    font-size: 14px;

    line-height: 1.65;
}

.footer-note {
    margin-top: 20px;

    color: #6F6C82;

    font-size: 11px;
}


/* =======================================================
   RESPONSIVE
   ======================================================= */

@media (max-width: 900px) {

    .home-stats {
        grid-template-columns: 1fr;
    }

    .stepper {
        flex-wrap: wrap;
    }

    .step {
        flex: none;
    }

    .greeting {
        font-size: 26px;
    }
}

</style>
""")


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    render_html("""
    <div class="brand">

        <div class="brand-icon">
            🛡️
        </div>

        <div class="brand-name">
            Goal<span>Safe</span> AI
        </div>

        <div class="brand-sub">
            Visual Safety Assistant
        </div>

    </div>

    <div class="side-label">
        MENUS
    </div>
    """)

    # Home
    if st.button(
        "🏠  Home",
        key="nav_home",
        width="stretch",
        type=(
            "primary"
            if st.session_state.current_page == "Home"
            else "secondary"
        ),
    ):
        st.session_state.current_page = "Home"
        st.rerun()

    # New Assessment
    if st.button(
        "＋  New Assessment",
        key="nav_new",
        width="stretch",
        type=(
            "primary"
            if st.session_state.current_page == "New Assessment"
            else "secondary"
        ),
    ):
        st.session_state.current_page = "New Assessment"

        st.session_state.assessment_result = None
        st.session_state.assessment_image = None
        st.session_state.assessment_evidence = None
        st.session_state.assessment_guidance = None
        st.session_state.assessment_decision = None
        st.session_state.assessment_saved = False

        st.session_state.assessment_reset += 1

        st.rerun()

    # History
    if st.button(
        "📋  Assessment History",
        key="nav_history",
        width="stretch",
        type=(
            "primary"
            if st.session_state.current_page == "Assessment History"
            else "secondary"
        ),
    ):
        st.session_state.current_page = "Assessment History"
        st.rerun()

    # Overview
    if st.button(
        "📊  Overview",
        key="nav_overview",
        width="stretch",
        type=(
            "primary"
            if st.session_state.current_page == "Overview"
            else "secondary"
        ),
    ):
        st.session_state.current_page = "Overview"
        st.rerun()


# =========================================================
# OVERVIEW PAGE
# =========================================================

if st.session_state.current_page == "Overview":

    history = st.session_state.assessment_history

    total = len(history)

    hazards = sum(
        1
        for item in history
        if item.get("decision") != "NO_HAZARD"
    )

    safe = total - hazards

    render_html("""
    <div class="greeting">
        Overview
    </div>

    <div class="header-subtitle">
        GoalSafe AI safety assessment summary
    </div>
    """)

    render_html(f"""
    <div class="home-stats">

        <div class="stat-card">
            <div class="stat-title">
                Total Assessments
            </div>

            <div class="stat-number">
                {total}
            </div>

            <div class="stat-sub">
                All time
            </div>
        </div>


        <div class="stat-card">
            <div class="stat-title">
                Hazards Found
            </div>

            <div class="stat-number red">
                {hazards}
            </div>

            <div class="stat-sub">
                Detected hazards
            </div>
        </div>


        <div class="stat-card">
            <div class="stat-title">
                Safe Scenes
            </div>

            <div class="stat-number green">
                {safe}
            </div>

            <div class="stat-sub">
                No relevant hazard
            </div>
        </div>

    </div>
    """)

    if total == 0:

        render_html("""
        <div class="result-card">

            <div class="result-card-title">
                No assessment data yet
            </div>

            <div class="result-text">
                Complete your first safety assessment to see
                your GoalSafe AI statistics here.
            </div>

        </div>
        """)

    else:

        render_html(f"""
        <div class="result-card">

            <div class="result-card-title">
                Assessment Summary
            </div>

            <div class="result-text">

                GoalSafe AI has completed
                <b>{total}</b> assessment(s).

                <br><br>

                <b>{hazards}</b> potential hazard(s) were identified.

                <br>

                <b>{safe}</b> scene(s) had no relevant visible hazard.

            </div>

        </div>
        """)

    st.stop()


# =========================================================
# ASSESSMENT HISTORY PAGE
# =========================================================

if st.session_state.current_page == "Assessment History":

    render_html("""
    <div class="greeting">
        Assessment History
    </div>

    <div class="header-subtitle">
        Your completed GoalSafe AI safety assessments
    </div>
    """)

    history = st.session_state.assessment_history

    if not history:

        render_html("""
        <div class="result-card">

            <div class="result-card-title">
                No assessments yet
            </div>

            <div class="result-text">
                Complete your first safety assessment and
                it will appear here.
            </div>

        </div>
        """)

    else:

        for item in reversed(history):

            if item.get("decision") == "NO_HAZARD":
                status = "✓ No Relevant Hazard"
            else:
                status = "⚠ Potential Hazard Detected"

            render_html(f"""
            <div class="assessment-card">

                <div class="assessment-time">
                    {html.escape(item["timestamp"])}
                </div>

                <div class="assessment-goal">
                    {html.escape(item["goal"])}
                </div>

                <div class="assessment-status">
                    {status}
                </div>

                <br>

                <div class="result-text">

                    <b>Finding:</b>
                    {html.escape(item["result"])}

                    <br><br>

                    <b>Guidance:</b>
                    {html.escape(item["guidance"])}

                </div>

            </div>
            """)

    st.stop()


# =========================================================
# HOME PAGE
# =========================================================

if st.session_state.current_page == "Home":

    history = st.session_state.assessment_history

    total = len(history)

    hazards = sum(
        1
        for item in history
        if item.get("decision") != "NO_HAZARD"
    )

    safe = total - hazards

    # Header
    render_html("""
    <div class="greeting">
        Hi, <span class="name"> Janani</span> 👋
    </div>

    <div class="header-subtitle">
        Goal-Driven Visual Safety Assessment
    </div>
    """)

    # Statistics
    render_html(f"""
    <div class="home-stats">

        <div class="stat-card">

            <div class="stat-title">
                Total Assessments
            </div>

            <div class="stat-number">
                {total}
            </div>

            <div class="stat-sub">
                All time
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-title">
                Hazards Found
            </div>

            <div class="stat-number red">
                {hazards}
            </div>

            <div class="stat-sub">
                All time
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-title">
                Safe Scenes
            </div>

            <div class="stat-number green">
                {safe}
            </div>

            <div class="stat-sub">
                All time
            </div>

        </div>

    </div>
    """)

    # Recent assessments
    render_html("""
    <div class="section-title">
        Recent Assessments
    </div>
    """)

    if not history:

        render_html("""
        <div class="result-card">

            <div class="result-card-title">
                No assessments yet
            </div>

            <div class="result-text">
                Start a new safety assessment from the sidebar.
            </div>

        </div>
        """)

    else:

        for item in reversed(history[-3:]):

            if item.get("decision") == "NO_HAZARD":
                status = "✓ No Relevant Hazard"
            else:
                status = "⚠ Potential Hazard"

            render_html(f"""
            <div class="assessment-card">

                <div class="assessment-time">
                    {html.escape(item["timestamp"])}
                </div>

                <div class="assessment-goal">
                    {html.escape(item["goal"])}
                </div>

                <div class="assessment-status">
                    {status}
                </div>

            </div>
            """)

    render_html("""
    <div class="footer-note">
        GoalSafe AI provides an AI-based visual assessment
        based on visible evidence and should not replace
        professional safety inspection.
    </div>
    """)

    st.stop()


# =========================================================
# NEW ASSESSMENT PAGE
# =========================================================

render_html("""
<div class="greeting">
    New Assessment
</div>

<div class="header-subtitle">
    Start a new GoalSafe AI visual safety assessment
</div>
""")

# =========================================================
# STEPPER
# =========================================================

render_html("""
<div class="stepper">

    <div class="step active">
        <div class="step-number">1</div>
        <span>Upload Scene</span>
    </div>

    <div class="step-arrow">→</div>

    <div class="step active">
        <div class="step-number">2</div>
        <span>Safety Goal</span>
    </div>

    <div class="step-arrow">→</div>

    <div class="step active">
        <div class="step-number">3</div>
        <span>AI Assessment</span>
    </div>

    <div class="step-arrow">→</div>

    <div class="step active">
        <div class="step-number">4</div>
        <span>Results</span>
    </div>

</div>
""")

# =========================================================
# INPUT AREA
# =========================================================

left, right = st.columns(
    [1, 1],
    gap="large"
)


# =========================================================
# UPLOAD
# =========================================================

with left:

    render_html("""
    <div class="input-card">

        <div class="input-title">
            Upload Scene
        </div>

        <div class="input-description">
            Add an image containing the area you want to assess.
        </div>

    </div>
    """)

    uploaded_image = st.file_uploader(
        "Upload Scene",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        key=f"scene_{st.session_state.assessment_reset}",
    )

    if uploaded_image is not None:

        image = Image.open(uploaded_image)

        st.image(
            image,
            width="stretch"
        )

        size_mb = uploaded_image.size / (1024 * 1024)

        st.caption(
            f"{uploaded_image.name} • {size_mb:.2f} MB"
        )


# =========================================================
# SAFETY GOAL
# =========================================================

with right:

    render_html("""
    <div class="input-card">

        <div class="input-title">
            Safety Concern / Goal
        </div>

        <div class="input-description">
            Describe exactly what you want to verify.
        </div>

    </div>
    """)

    user_goal = st.text_area(
        "Safety Concern / Goal",

        placeholder=(
            "Example: Check this area for trip hazards "
            "and unsafe objects."
        ),

        height=155,

        label_visibility="collapsed",

        key=f"goal_{st.session_state.assessment_reset}",
    )

    assess_button = st.button(
        "✦  Assess Safety",
        width="stretch",
        type="primary",
    )


# =========================================================
# RUN ASSESSMENT
# =========================================================

if assess_button:

    if uploaded_image is None:

        st.warning(
            "Please upload an image before assessing."
        )

    elif not user_goal.strip():

        st.warning(
            "Please enter a safety concern or goal."
        )

    else:

        try:

            with st.spinner(
                "GoalSafe AI is assessing the scene..."
            ):

                image_bytes = uploaded_image.getvalue()

                result, decision = assess_image(
                    image_bytes,
                    user_goal
                )

                assessment_image = Image.open(
                    io.BytesIO(image_bytes)
                ).copy()

                st.session_state.assessment_result = result

                st.session_state.assessment_evidence = (
                    getattr(result, "evidence", None)
                )

                st.session_state.assessment_guidance = (
                    getattr(result, "guidance", None)
                )

                st.session_state.assessment_decision = decision

                st.session_state.assessment_image = (
                    assessment_image
                )

                # Save completed assessment once
                if not st.session_state.assessment_saved:

                    finding = (
                        getattr(
                            result,
                            "condition_description",
                            None
                        )
                        or getattr(
                            result,
                            "goal_relevant_fact",
                            None
                        )
                        or getattr(
                            result,
                            "finding",
                            None
                        )
                        or "No relevant hazard detected."
                    )

                    guidance = (
                        getattr(
                            result,
                            "guidance",
                            None
                        )
                        or
                        "No corrective action is indicated "
                        "based on the visible evidence."
                    )

                    st.session_state.assessment_history.append(
                        {
                            "timestamp": datetime.now().strftime(
                                "%d %b %Y, %I:%M %p"
                            ),

                            "goal": user_goal.strip(),

                            "result": finding,

                            "evidence": (
                                getattr(
                                    result,
                                    "evidence",
                                    None
                                )
                                or finding
                            ),

                            "guidance": guidance,

                            "decision": decision,
                        }
                    )

                    st.session_state.assessment_saved = True

        except Exception as error:

            st.error(
                "Assessment failed."
            )

            st.exception(error)


# =========================================================
# RESULT
# =========================================================

if st.session_state.assessment_result:

    result = st.session_state.assessment_result

    decision = st.session_state.assessment_decision

    result_image = st.session_state.assessment_image

    finding_text = (
        getattr(
            result,
            "condition_description",
            None
        )
        or getattr(
            result,
            "goal_relevant_fact",
            None
        )
        or getattr(
            result,
            "finding",
            None
        )
        or "No relevant hazard detected."
    )

    evidence_text = (
        getattr(
            result,
            "evidence",
            None
        )
        or getattr(
            result,
            "condition_description",
            None
        )
        or getattr(
            result,
            "goal_relevant_fact",
            None
        )
        or "No visible evidence was identified."
    )

    guidance_text = (
        st.session_state.assessment_guidance
        or
        "No corrective action is indicated based "
        "on the visible evidence."
    )

    condition_text = (
        getattr(
            result,
            "condition",
            None
        )
        or
        finding_text
    )


    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    if decision == "NO_HAZARD":

        result_heading = "No Relevant Hazard Detected"
        result_icon = "✓"

    else:

        result_heading = "Potential Hazard Detected"
        result_icon = "⚠"


    # -----------------------------------------------------
    # RESULT HEADER
    # -----------------------------------------------------

    render_html(f"""
    <div class="result-title">
        ✦ &nbsp; AI Assessment Result
    </div>

    <div class="result-banner">

        <div class="result-icon">
            {result_icon}
        </div>

        <div>

            <div class="result-heading">
                {html.escape(result_heading)}
            </div>

            <div class="result-description">
                {html.escape(str(condition_text))}
            </div>

        </div>

    </div>
    """)


    # -----------------------------------------------------
    # RESULT CARDS
    # -----------------------------------------------------

    finding_col, evidence_col, guidance_col = st.columns(
        [1, 1.15, 1],
        gap="medium"
    )


    # Finding
    with finding_col:

        render_html(f"""
        <div class="result-card">

            <div class="result-card-title">
                ⚠ &nbsp; Hazard Finding
            </div>

            <div class="result-text">
                {html.escape(str(finding_text))}
            </div>

        </div>
        """)


    # Evidence
    with evidence_col:

        render_html(f"""
        <div class="result-card">

            <div class="result-card-title">
                ◉ &nbsp; Visual Evidence
            </div>

            <div class="result-text">
                {html.escape(str(evidence_text))}
            </div>

        </div>
        """)

        if result_image is not None:

            st.image(
                result_image,
                width="stretch"
            )


    # Guidance
    with guidance_col:

        render_html(f"""
        <div class="result-card">

            <div class="result-card-title">
                ✓ &nbsp; Safety Guidance
            </div>

            <div class="result-text">
                {html.escape(str(guidance_text))}
            </div>

        </div>
        """)


# =========================================================
# FOOTER
# =========================================================

render_html("""
<div class="footer-note">

    GoalSafe AI provides an AI-based visual assessment
    based on visible evidence and should not replace
    professional safety inspection.

</div>
""")