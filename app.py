import streamlit as st
import os
import uuid

from core.dicom_to_nrrd import convert_dicom_to_nrrd
from core.segment import run_segmentation
from core.metrics import run_metrics
from core.visualize import show_slices
from core.export import save_medical_volumes, save_preview_image, save_excel
from core.gender_prediction import predict_gender


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CBCT Sinus AI Analyzer",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DARK UI CSS
# ============================================================

st.markdown("""
<style>
/* ================= GLOBAL ================= */

.stApp {
    background: #0b1120;
    color: #f8fafc;
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}


/* ================= SIDEBAR ================= */

[data-testid="stSidebar"] {
    background: #070d1a;
    border-right: 1px solid #1e293b;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #e2e8f0 !important;
}


/* ================= HERO ================= */

.hero {
    background: linear-gradient(
        135deg,
        #111827 0%,
        #172554 50%,
        #0f766e 100%
    );

    border: 1px solid #334155;
    border-radius: 22px;
    padding: 38px 42px;
    margin-bottom: 35px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.35);
}

.hero-title {
    color: #f8fafc;
    font-size: 38px;
    font-weight: 800;
    margin: 0;
}

.hero-subtitle {
    color: #cbd5e1;
    font-size: 16px;
    margin-top: 10px;
}

.hero-badge {
    display: inline-block;
    margin-top: 18px;
    padding: 7px 14px;
    border-radius: 20px;
    background: rgba(56,189,248,0.12);
    border: 1px solid rgba(56,189,248,0.25);
    color: #7dd3fc;
    font-size: 13px;
}


/* ================= HEADINGS ================= */

.section-title {
    color: #f8fafc;
    font-size: 25px;
    font-weight: 750;
    margin-top: 30px;
    margin-bottom: 6px;
}

.section-subtitle {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 20px;
}


/* ================= INPUT CARD ================= */

.input-card {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 20px;
}

.input-title {
    color: #f8fafc;
    font-size: 18px;
    font-weight: 700;
}

.input-description {
    color: #94a3b8;
    font-size: 13px;
    margin-top: 5px;
}


/* ================= RADIO BUTTON ================= */

.stRadio label {
    color: #e2e8f0 !important;
}

.stRadio p {
    color: #cbd5e1 !important;
}


/* ================= FILE UPLOADER ================= */

[data-testid="stFileUploader"] {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 10px;
}

[data-testid="stFileUploader"] section {
    background: #111827 !important;
}

[data-testid="stFileUploader"] label {
    color: #e2e8f0 !important;
}

[data-testid="stFileUploader"] small {
    color: #94a3b8 !important;
}


/* ================= BUTTON ================= */

.stButton > button {
    border-radius: 10px;
    min-height: 45px;
    font-weight: 700;
}


/* ================= RESULT CARD ================= */

.result-card {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 22px;
    min-height: 170px;
}

.result-title {
    color: #38bdf8;
    font-size: 17px;
    font-weight: 750;
    margin-bottom: 12px;
}


/* ================= PREDICTION ================= */

.prediction-card {
    background: linear-gradient(
        135deg,
        #0f172a,
        #12343b
    );

    border: 1px solid #155e75;
    border-radius: 18px;
    padding: 32px;
    text-align: center;
    margin-top: 10px;
}

.prediction-label {
    color: #67e8f9;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

.prediction-value {
    color: #f8fafc;
    font-size: 38px;
    font-weight: 800;
    margin: 8px 0;
}

.prediction-confidence {
    color: #cbd5e1;
    font-size: 15px;
}


/* ================= STATUS ================= */

.status-card {
    background: #052e2b;
    border: 1px solid #0f766e;
    border-radius: 12px;
    padding: 14px 18px;
    color: #99f6e4;
    font-weight: 650;
    margin: 20px 0;
}


/* ================= FOOTER ================= */

.footer {
    text-align: center;
    color: #64748b;
    font-size: 12px;
    margin-top: 50px;
    padding-top: 25px;
    border-top: 1px solid #1e293b;
}


/* ================= EXPANDER ================= */

[data-testid="stExpander"] {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 14px;
}


/* ================= JSON ================= */

[data-testid="stJson"] {
    background: #0b1120;
    border-radius: 10px;
}


/* ================= SUCCESS / INFO ================= */

.stAlert {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "nrrd_path": None,
    "seg_path": None,
    "left": None,
    "right": None,
    "analysis_done": False,
    "gender": None,
    "gender_prob": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "<div style='text-align:center;'>"
        "<div style='font-size:48px;'>🦷</div>"
        "<h2>SINUS AI</h2>"
        "<p style='color:#64748b;'>CBCT Analysis Platform</p>"
        "</div>",
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### ANALYSIS PIPELINE")

    st.markdown("""
**01**  Upload Scan

**02**  Preprocessing

**03**  3D Segmentation

**04**  Extract Metrics

**05**  Gender Prediction

**06**  Generate Report
""")

    st.divider()

    st.markdown("### INPUT TYPES")

    st.caption("DICOM / DCM")
    st.caption("NRRD")

    st.divider()

    st.caption("CBCT Sinus AI Analyzer")
    st.caption("Academic / Research Prototype")


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">
<div class="hero-title">🦷 CBCT Sinus AI Analyzer</div>
<div class="hero-subtitle">
Automated maxillary sinus segmentation, measurement and
gender prediction from CBCT scans.
</div>
<div class="hero-badge">
3D U-Net&nbsp;&nbsp;•&nbsp;&nbsp;Image Segmentation&nbsp;&nbsp;•&nbsp;&nbsp;ML Prediction
</div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# INPUT
# ============================================================

st.markdown(
    '<div class="section-title">📁 Upload Medical Scan</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">'
    'Select your scan format and upload the required files.'
    '</div>',
    unsafe_allow_html=True
)


mode = st.radio(
    "Input Type",
    ["Upload DICOM Folder", "Upload NRRD File"],
    horizontal=True,
    label_visibility="collapsed"
)

os.makedirs("temp", exist_ok=True)


# ============================================================
# DICOM
# ============================================================

if mode == "Upload DICOM Folder":

    st.markdown("""
<div class="input-card">
<div class="input-title">📂 DICOM Scan</div>
<div class="input-description">
Upload all DICOM slices belonging to the CBCT scan.
</div>
</div>
""", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload DICOM files",
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:

        st.success(
            f"✓ {len(uploaded_files)} DICOM file(s) uploaded"
        )

        case_id = str(uuid.uuid4())[:8]

        case_folder = os.path.join(
            "temp",
            case_id
        )

        os.makedirs(case_folder, exist_ok=True)

        dicom_folder = os.path.join(
            case_folder,
            "dicom"
        )

        os.makedirs(dicom_folder, exist_ok=True)

        for file in uploaded_files:

            with open(
                os.path.join(
                    dicom_folder,
                    file.name
                ),
                "wb"
            ) as f:

                f.write(file.getbuffer())


        if st.button(
            "🚀  RUN AI ANALYSIS",
            use_container_width=True,
            type="primary"
        ):

            progress = st.progress(0)

            with st.spinner("Converting DICOM → NRRD..."):

                st.session_state.nrrd_path = (
                    convert_dicom_to_nrrd(
                        dicom_folder,
                        case_folder
                    )
                )

            progress.progress(25)

            seg_out = os.path.join(
                case_folder,
                "seg.seg.nrrd"
            )

            with st.spinner(
                "Running 3D AI segmentation..."
            ):

                st.session_state.seg_path = (
                    run_segmentation(
                        st.session_state.nrrd_path,
                        seg_out
                    )
                )

            progress.progress(60)

            with st.spinner(
                "Calculating sinus metrics..."
            ):

                (
                    st.session_state.left,
                    st.session_state.right
                ) = run_metrics(
                    st.session_state.seg_path
                )

            progress.progress(80)

            measurements = {}

            if st.session_state.left:
                measurements["Left"] = (
                    st.session_state.left
                )

            if st.session_state.right:
                measurements["Right"] = (
                    st.session_state.right
                )

            with st.spinner(
                "Running gender prediction..."
            ):

                gender, prob = predict_gender(
                    measurements
                )

                st.session_state.gender = gender
                st.session_state.gender_prob = prob

            progress.progress(100)

            st.session_state.analysis_done = True

            st.success("✓ Analysis Complete")


# ============================================================
# NRRD
# ============================================================

else:

    st.markdown("""
<div class="input-card">
<div class="input-title">🧠 NRRD Volume</div>
<div class="input-description">
Upload a pre-converted NRRD medical volume.
</div>
</div>
""", unsafe_allow_html=True)

    uploaded_nrrd = st.file_uploader(
        "Upload NRRD",
        type=["nrrd"],
        label_visibility="collapsed"
    )

    if uploaded_nrrd:

        st.success(
            f"✓ {uploaded_nrrd.name} uploaded"
        )

        case_id = str(uuid.uuid4())[:8]

        case_folder = os.path.join(
            "temp",
            case_id
        )

        os.makedirs(case_folder, exist_ok=True)

        nrrd_path = os.path.join(
            case_folder,
            uploaded_nrrd.name
        )

        with open(nrrd_path, "wb") as f:
            f.write(uploaded_nrrd.getbuffer())


        if st.button(
            "🚀  RUN AI ANALYSIS",
            use_container_width=True,
            type="primary"
        ):

            progress = st.progress(0)

            st.session_state.nrrd_path = nrrd_path

            seg_out = os.path.join(
                case_folder,
                "seg.seg.nrrd"
            )

            with st.spinner(
                "Running 3D AI segmentation..."
            ):

                st.session_state.seg_path = (
                    run_segmentation(
                        nrrd_path,
                        seg_out
                    )
                )

            progress.progress(50)

            with st.spinner(
                "Calculating sinus metrics..."
            ):

                (
                    st.session_state.left,
                    st.session_state.right
                ) = run_metrics(
                    st.session_state.seg_path
                )

            progress.progress(75)

            measurements = {}

            if st.session_state.left:
                measurements["Left"] = (
                    st.session_state.left
                )

            if st.session_state.right:
                measurements["Right"] = (
                    st.session_state.right
                )

            with st.spinner(
                "Running gender prediction..."
            ):

                gender, prob = predict_gender(
                    measurements
                )

                st.session_state.gender = gender
                st.session_state.gender_prob = prob

            progress.progress(100)

            st.session_state.analysis_done = True

            st.success("✓ Analysis Complete")


# ============================================================
# RESULTS
# ============================================================

if st.session_state.analysis_done:

    nrrd_path = st.session_state.nrrd_path
    seg_path = st.session_state.seg_path

    left = st.session_state.left
    right = st.session_state.right


    # ========================================================
    # STATUS
    # ========================================================

    st.markdown("""
<div class="status-card">
✓ Analysis completed successfully
</div>
""", unsafe_allow_html=True)


    # ========================================================
    # MEASUREMENTS
    # ========================================================

    st.markdown(
        '<div class="section-title">📊 Sinus Measurements</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Measurements extracted from the segmented maxillary sinuses.'
        '</div>',
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(2)


    with col1:

        st.markdown("""
<div class="result-card">
<div class="result-title">◀ LEFT MAXILLARY SINUS</div>
</div>
""", unsafe_allow_html=True)

        if left:
            st.json(left)
        else:
            st.warning(
                "Left sinus measurements unavailable."
            )


    with col2:

        st.markdown("""
<div class="result-card">
<div class="result-title">RIGHT MAXILLARY SINUS ▶</div>
</div>
""", unsafe_allow_html=True)

        if right:
            st.json(right)
        else:
            st.warning(
                "Right sinus measurements unavailable."
            )


    # ========================================================
    # GENDER
    # ========================================================

    st.markdown(
        '<div class="section-title">🧬 Gender Prediction</div>',
        unsafe_allow_html=True
    )

    if st.session_state.gender:

        probability = st.session_state.gender_prob

        if probability is not None:
            confidence = f"{probability:.2f}"
        else:
            confidence = "N/A"

        st.markdown(
            f"""
<div class="prediction-card">
<div class="prediction-label">
MODEL PREDICTION
</div>

<div class="prediction-value">
{st.session_state.gender}
</div>

<div class="prediction-confidence">
Confidence: <b>{confidence}</b>
</div>
</div>
""",
            unsafe_allow_html=True
        )

    else:

        st.warning(
            "Gender could not be predicted "
            "(Volume < 2000 mm³)."
        )


    # ========================================================
    # VISUALIZATION
    # ========================================================

    st.markdown(
        '<div class="section-title">🧠 Segmentation Visualization</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Explore the CBCT volume and AI-generated segmentation.'
        '</div>',
        unsafe_allow_html=True
    )

    with st.expander(
        "🔬 OPEN SCAN VIEWER",
        expanded=True
    ):

        show_slices(
            nrrd_path,
            seg_path
        )


    # ========================================================
    # EXPORT
    # ========================================================

    st.markdown(
        '<div class="section-title">💾 Patient Report</div>',
        unsafe_allow_html=True
    )

    patient_folder = os.path.join(
        "results",
        os.path.basename(nrrd_path).split(".")[0]
    )

    os.makedirs(
        "results",
        exist_ok=True
    )

    with st.spinner(
        "Preparing patient report..."
    ):

        save_medical_volumes(
            nrrd_path,
            seg_path,
            patient_folder
        )

        save_preview_image(
            nrrd_path,
            seg_path,
            patient_folder
        )

        excel_path = save_excel(
            left,
            right,
            st.session_state.gender,
            st.session_state.gender_prob,
            patient_folder
        )

    st.success(
        "✓ Results saved successfully"
    )

    with open(excel_path, "rb") as f:

        st.download_button(
            "📥 DOWNLOAD EXCEL REPORT",
            f,
            file_name="measurements.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
CBCT Sinus AI Analyzer<br>
3D U-Net Segmentation • Machine Learning Prediction<br>
Academic / Research Prototype
</div>
""", unsafe_allow_html=True)