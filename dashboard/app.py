"""
Veracity Agent – Dashboard v2
Dark premium UI | Tabbed layout | Multi-issuer | Batch | Photo/Video/Excel previews
"""

import streamlit as st
import requests
import pandas as pd
import base64
import time
import json
from io import BytesIO
from PIL import Image

# ──────────────────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────────────────
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Veracity Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# Custom CSS – dark premium theme
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global ──────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0d14;
    color: #e2e8f0;
}

/* ── Page background ─────────────────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, #0a0d14 0%, #0f1520 50%, #0a0d14 100%);
    min-height: 100vh;
}

/* ── Sidebar ─────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #111827 100%);
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #4f8ef7;
}

/* ── Tabs ─────────────────────────────────────────────────────── */
div[data-testid="stTabs"] > div > div > div > button {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: #64748b;
    font-weight: 500;
    padding: 0.6rem 1.2rem;
    transition: all 0.2s ease;
    font-size: 0.9rem;
}
div[data-testid="stTabs"] > div > div > div > button:hover {
    color: #a5b4fc;
    border-bottom-color: #4f8ef7;
}
div[data-testid="stTabs"] > div > div > div > button[aria-selected="true"] {
    color: #4f8ef7 !important;
    border-bottom: 2px solid #4f8ef7 !important;
    font-weight: 700;
}

/* ── Cards / containers ───────────────────────────────────────── */
div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
    background: rgba(255,255,255,0.02);
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
}

/* ── Buttons ─────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #4f8ef7, #7c3aed);
    color: #fff !important;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    font-size: 0.88rem;
    transition: all 0.25s ease;
    box-shadow: 0 4px 15px rgba(79,142,247,0.25);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(79,142,247,0.4);
}

/* ── File uploader ───────────────────────────────────────────── */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(79,142,247,0.05) !important;
    border: 2px dashed #334155 !important;
    border-radius: 12px !important;
    transition: border-color 0.25s;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #4f8ef7 !important;
}

/* ── Metrics ─────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 1rem;
}
[data-testid="stMetricValue"] {
    color: #4f8ef7 !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

/* ── Select / dropdown ───────────────────────────────────────── */
div[data-testid="stSelectbox"] > div {
    border: 1px solid #334155 !important;
    background: #111827 !important;
    border-radius: 8px;
    color: #e2e8f0;
}

/* ── Dataframe ───────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #1e293b;
    border-radius: 10px;
    overflow: hidden;
}

/* ── Alerts / info boxes ─────────────────────────────────────── */
.stAlert > div {
    border-radius: 10px;
    border: none;
}

/* ── Code/JSON ───────────────────────────────────────────────── */
.stJson {
    background: #0d1117 !important;
    border-radius: 8px;
    border: 1px solid #1e293b;
}

/* ── Expander ────────────────────────────────────────────────── */
details {
    background: rgba(255,255,255,0.02);
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 0.3rem 0.8rem;
}
summary {
    font-weight: 500;
    cursor: pointer;
    color: #94a3b8;
}

/* ── Divider ─────────────────────────────────────────────────── */
hr { border-color: #1e293b !important; }

/* ──  Badge styles (rendered via html) ──────────────────────── */
.badge-verified {
    display: inline-block;
    background: linear-gradient(135deg, #065f46, #047857);
    color: #6ee7b7;
    border: 1px solid #047857;
    border-radius: 20px;
    padding: 0.35rem 1.1rem;
    font-weight: 700;
    font-size: 0.95rem;
    letter-spacing: 0.05em;
}
.badge-tampered {
    display: inline-block;
    background: linear-gradient(135deg, #7c2d12, #b45309);
    color: #fcd34d;
    border: 1px solid #b45309;
    border-radius: 20px;
    padding: 0.35rem 1.1rem;
    font-weight: 700;
    font-size: 0.95rem;
    letter-spacing: 0.05em;
}
.badge-revoked {
    display: inline-block;
    background: linear-gradient(135deg, #1e1b4b, #4c1d95);
    color: #c4b5fd;
    border: 1px solid #6d28d9;
    border-radius: 20px;
    padding: 0.35rem 1.1rem;
    font-weight: 700;
    font-size: 0.95rem;
    letter-spacing: 0.05em;
}
.badge-rejected {
    display: inline-block;
    background: linear-gradient(135deg, #7f1d1d, #991b1b);
    color: #fca5a5;
    border: 1px solid #dc2626;
    border-radius: 20px;
    padding: 0.35rem 1.1rem;
    font-weight: 700;
    font-size: 0.95rem;
    letter-spacing: 0.05em;
}

/* ── Logo / header ───────────────────────────────────────────── */
.va-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem 0 1rem 0;
    border-bottom: 1px solid #1e293b;
    margin-bottom: 1.5rem;
}
.va-title {
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #4f8ef7, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
}
.va-subtitle {
    color: #64748b;
    font-size: 0.85rem;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def api(method: str, path: str, **kwargs):
    """Generic API call with graceful error handling."""
    try:
        fn = getattr(requests, method)
        resp = fn(f"{API_BASE}{path}", **kwargs)
        return resp
    except requests.exceptions.ConnectionError:
        return None


def status_badge(status: str) -> str:
    s = status.upper()
    if "VERIFIED" in s:
        return '<span class="badge-verified">✅ VERIFIED</span>'
    elif "REVOKED" in s:
        return '<span class="badge-revoked">🔒 REVOKED</span>'
    elif "REJECTED" in s:
        return '<span class="badge-rejected">❌ REJECTED</span>'
    else:
        return '<span class="badge-tampered">⚠️ TAMPERED / UNKNOWN</span>'


def file_type_icon(category: str) -> str:
    icons = {
        "image":        "🖼️",
        "video":        "🎬",
        "document":     "📄",
        "spreadsheet":  "📊",
        "presentation": "📑",
        "other":        "📁",
    }
    return icons.get(category, "📁")


def fetch_issuers():
    resp = api("get", "/issuers")
    if resp and resp.ok:
        return {i["did"]: f'{i["short"]} — {i["name"]}' for i in resp.json()["issuers"]}
    return {"did:veracity:mlritm": "MLRITM — MLR Institute of Technology and Management"}


def show_file_preview(uploaded_file):
    """Show image/video/spreadsheet preview before registration."""
    name = uploaded_file.name.lower()
    ext  = name.rsplit(".", 1)[-1] if "." in name else ""

    # Image preview
    if ext in ("jpg", "jpeg", "png", "gif", "bmp", "webp"):
        try:
            img = Image.open(BytesIO(uploaded_file.getvalue()))
            st.image(img, caption=uploaded_file.name, use_container_width=True)
            w, h = img.size
            st.caption(f"Dimensions: {w} × {h} px | Mode: {img.mode}")
        except Exception:
            st.info("Image preview unavailable")

    # Video – just show file info
    elif ext in ("mp4", "avi", "mov", "mkv", "webm"):
        size_mb = round(len(uploaded_file.getvalue()) / (1024 * 1024), 2)
        st.info(f"🎬 Video file detected — **{uploaded_file.name}** ({size_mb} MB)")

    # Spreadsheet preview via API
    elif ext in ("xlsx", "xls", "csv"):
        with st.spinner("Parsing spreadsheet…"):
            resp = api(
                "post", "/parse/spreadsheet",
                files={"file": (uploaded_file.name, uploaded_file.getvalue())}
            )
            if resp and resp.ok:
                data = resp.json()
                if data.get("error"):
                    st.warning(f"Parse warning: {data['error']}")
                else:
                    st.caption(f"📊 **{data['total_sheets']} sheet(s) detected**")
                    for sheet in data["sheets"]:
                        with st.expander(f"Sheet: {sheet['name']} — {sheet['row_count']} rows × {sheet['col_count']} cols"):
                            if sheet.get("preview"):
                                headers = sheet["preview"][0] if sheet["preview"] else []
                                rows    = sheet["preview"][1:] if len(sheet["preview"]) > 1 else sheet["preview"]
                                try:
                                    if headers and rows:
                                        df = pd.DataFrame(rows, columns=headers)
                                    else:
                                        df = pd.DataFrame(sheet["preview"])
                                    st.dataframe(df, use_container_width=True)
                                except Exception:
                                    st.write(sheet["preview"])
                            st.code(f"SHA-256: {sheet['hash']}", language=None)


def show_verify_result(result: dict):
    """Render a rich verification result card."""
    status = result.get("status", "UNKNOWN")
    st.markdown(status_badge(status), unsafe_allow_html=True)
    st.markdown("")

    cols = st.columns(3)
    if result.get("issuer_name"):
        cols[0].markdown(f"**Issuer**  \n{result['issuer_name']}")
    if result.get("issuer"):
        cols[1].markdown(f"**DID**  \n`{result['issuer']}`")
    if result.get("latency_ms") is not None:
        cols[2].markdown(f"**Latency**  \n{result['latency_ms']} ms")

    if result.get("integrity"):
        st.success(f"🔐 Integrity: **{result['integrity']}** | Authenticity: **{result['authenticity']}** | Provenance: **{result['provenance']}**")
    if result.get("reason"):
        st.error(f"⚠️ Reason: {result['reason']}")
    if result.get("file_type"):
        st.caption(f"{file_type_icon(result['file_type'])} File type: **{result['file_type']}** | MIME: `{result.get('mime_type','')}`")
    if result.get("issued_at"):
        import datetime
        ts = datetime.datetime.fromtimestamp(result["issued_at"]).strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"📅 Issued at: {ts}")


# ──────────────────────────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────────────────────────
if "latencies" not in st.session_state:
    st.session_state.latencies = []
if "op_log" not in st.session_state:
    st.session_state.op_log = []   # list of {"op", "file", "ts", "status"}


# ──────────────────────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="va-header">
  <div style="font-size:2.5rem">🛡️</div>
  <div>
    <p class="va-title">Veracity Agent</p>
    <p class="va-subtitle">Autonomous AI Trust &amp; Document Integrity System</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar – status + quick info
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌐 System Status")

    ping = api("get", "/issuers")
    if ping and ping.ok:
        st.success("Backend Online")
        issuers_map = {i["did"]: f'{i["short"]}' for i in ping.json()["issuers"]}
        issuer_options = {i["did"]: f'{i["short"]} — {i["name"]}' for i in ping.json()["issuers"]}
    else:
        st.error("Backend Offline – start the API server")
        issuers_map = {}
        issuer_options = {}

    st.markdown("---")
    st.markdown("## 🏛️ Trusted Issuers")
    if issuer_options:
        for did, label in issuer_options.items():
            colour_map = {
                "did:veracity:mlritm":   "#4f8ef7",
                "did:veracity:external": "#34d399",
                "did:veracity:govt":     "#f59e0b",
            }
            c = colour_map.get(did, "#94a3b8")
            short = did.split(":")[-1].upper()
            st.markdown(
                f'<div style="border-left:3px solid {c}; padding:0.3rem 0.6rem; margin-bottom:0.4rem; border-radius:4px; background:rgba(255,255,255,0.02)">'
                f'<span style="color:{c};font-weight:700;font-size:0.8rem">{short}</span><br>'
                f'<span style="color:#94a3b8;font-size:0.75rem">{did}</span>'
                f'</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 📋 Quick Stats")
    ledger_resp = api("get", "/ledger/view")
    if ledger_resp and ledger_resp.ok:
        records = ledger_resp.json().get("records", [])
        total   = len(records)
        revoked = sum(1 for r in records if r.get("revoked"))
        col1, col2 = st.columns(2)
        col1.metric("Registered", total)
        col2.metric("Revoked", revoked)

    chain_resp = api("get", "/blockchain/verify")
    if chain_resp and chain_resp.ok:
        valid = chain_resp.json().get("blockchain_valid", False)
        if valid:
            st.success("⛓️ Chain: Intact")
        else:
            st.error("⛓️ Chain: Compromised!")

    st.markdown("---")
    st.caption("v2.0 | RSA-PSS-SHA256")


# ──────────────────────────────────────────────────────────────────────────────
# Tabs
# ──────────────────────────────────────────────────────────────────────────────
tab_register, tab_verify, tab_batch, tab_ledger, tab_blockchain, tab_analytics = st.tabs([
    "✍️  Register",
    "🔍  Verify",
    "📦  Batch",
    "📘  Ledger",
    "⛓️  Blockchain",
    "📊  Analytics",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – REGISTER
# ══════════════════════════════════════════════════════════════════════════════
with tab_register:
    st.markdown("### ✍️ Register & Sign a Document")
    st.markdown(
        "Upload a file, choose the **issuer** that will sign it, and anchor it to the blockchain. "
        "Supported: PDFs, images (JPG/PNG), videos (MP4), Excel/CSV, Word docs, and more."
    )

    col_up, col_opt = st.columns([2, 1])

    with col_up:
        reg_file = st.file_uploader(
            "Drop or select a file",
            key="reg_single",
            label_visibility="collapsed",
        )

    with col_opt:
        chosen_issuer = st.selectbox(
            "Signing Issuer",
            options=list(issuer_options.keys()),
            format_func=lambda did: issuer_options.get(did, did),
            key="reg_issuer",
        ) if issuer_options else None

    if reg_file:
        st.markdown("#### 👁️ Preview")
        show_file_preview(reg_file)
        st.markdown("")

        col_btn, col_info = st.columns([1, 3])
        with col_btn:
            do_register = st.button("🔐 Register & Sign", key="btn_register")

        if do_register and chosen_issuer:
            with st.spinner("Signing and anchoring…"):
                resp = api(
                    "post", "/upload",
                    files={"file": (reg_file.name, reg_file.getvalue())},
                    data={"issuer_did": chosen_issuer},
                )

            if resp is None:
                st.error("Could not reach backend. Is the API running?")
            elif resp.ok:
                result = resp.json()
                st.success(f"✅ **{reg_file.name}** registered successfully!")

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("File Type", f"{file_type_icon(result.get('file_type',''))} {result.get('file_type','—')}")
                c2.metric("Block Index", result.get("block_index", "—"))
                c3.metric("Latency", f"{result.get('upload_latency_ms','—')} ms")
                size = result.get("size_bytes", 0)
                c4.metric("Size", f"{round(size/1024, 1)} KB" if size else "—")

                with st.expander("📄 Full Registration Record"):
                    display = {k: v for k, v in result.items() if k != "spreadsheet_info"}
                    st.json(display)

                if "spreadsheet_info" in result:
                    with st.expander("📊 Spreadsheet Analysis"):
                        info = result["spreadsheet_info"]
                        for sheet in info.get("sheets", []):
                            st.markdown(f"**{sheet['name']}** — {sheet['row_count']} rows, {sheet['col_count']} cols")
                            st.code(f"Sheet Hash: {sheet['hash']}", language=None)

                st.session_state.op_log.append({
                    "op": "Register", "file": reg_file.name,
                    "ts": time.strftime("%H:%M:%S"), "status": "OK",
                    "issuer": issuers_map.get(chosen_issuer, chosen_issuer),
                })
            else:
                try:
                    err = resp.json().get("detail", resp.text)
                except Exception:
                    err = resp.text
                st.error(f"❌ Registration failed: {err}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 – VERIFY
# ══════════════════════════════════════════════════════════════════════════════
with tab_verify:
    st.markdown("### 🔍 Verify a Document")
    st.markdown(
        "Upload any file to check its integrity, authenticity, and provenance. "
        "The system checks against the ledger and verifies the issuer's digital signature."
    )

    ver_file = st.file_uploader(
        "Drop or select a file to verify",
        key="ver_single",
        label_visibility="collapsed",
    )

    if ver_file:
        show_file_preview(ver_file)
        st.markdown("")

        col_vbtn, _ = st.columns([1, 3])
        with col_vbtn:
            do_verify = st.button("🔍 Verify Document", key="btn_verify")

        if do_verify:
            with st.spinner("Verifying…"):
                resp = api(
                    "post", "/verify",
                    files={"file": (ver_file.name, ver_file.getvalue())},
                )

            if resp is None:
                st.error("Could not reach backend.")
            else:
                result = resp.json()
                show_verify_result(result)

                lat = result.get("latency_ms")
                if lat is not None:
                    st.session_state.latencies.append(lat)

                st.session_state.op_log.append({
                    "op": "Verify", "file": ver_file.name,
                    "ts": time.strftime("%H:%M:%S"),
                    "status": result.get("status", "?"),
                    "issuer": issuers_map.get(result.get("issuer", ""), "—"),
                })


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – BATCH
# ══════════════════════════════════════════════════════════════════════════════
with tab_batch:
    st.markdown("### 📦 Batch Operations")
    batch_mode = st.radio("Mode", ["Register batch", "Verify batch"], horizontal=True, label_visibility="collapsed")

    if batch_mode == "Register batch":
        st.markdown("Upload **multiple files** at once. All will be signed by the chosen issuer.")

        col_bf, col_bi = st.columns([2, 1])
        with col_bf:
            batch_files = st.file_uploader(
                "Select files",
                accept_multiple_files=True,
                key="batch_reg",
                label_visibility="collapsed",
            )
        with col_bi:
            batch_issuer = st.selectbox(
                "Issuer",
                options=list(issuer_options.keys()),
                format_func=lambda did: issuer_options.get(did, did),
                key="batch_issuer",
            ) if issuer_options else None

        if batch_files:
            st.caption(f"{len(batch_files)} file(s) selected")
            col_bb, _ = st.columns([1, 3])
            with col_bb:
                do_batch_reg = st.button("🔐 Register All", key="btn_batch_reg")

            if do_batch_reg and batch_issuer:
                with st.spinner(f"Registering {len(batch_files)} files…"):
                    files_payload = [("files", (f.name, f.getvalue())) for f in batch_files]
                    resp = api(
                        "post", "/upload/batch",
                        files=files_payload,
                        data={"issuer_did": batch_issuer},
                    )

                if resp is None:
                    st.error("Backend unreachable.")
                elif resp.ok:
                    data = resp.json()
                    results = data.get("results", [])
                    st.success(f"Batch complete — **{len(results)}** files processed")

                    # Summary metrics
                    registered = sum(1 for r in results if r["status"] == "REGISTERED")
                    duplicates = sum(1 for r in results if r["status"] == "DUPLICATE")
                    failed     = sum(1 for r in results if r["status"] in ("FAILED", "ERROR"))
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Registered", registered)
                    c2.metric("Duplicate",  duplicates)
                    c3.metric("Failed",     failed)

                    # Results table
                    df_rows = []
                    for r in results:
                        df_rows.append({
                            "File":       r.get("filename", ""),
                            "Status":     r.get("status", ""),
                            "Type":       f"{file_type_icon(r.get('file_type',''))} {r.get('file_type','—')}",
                            "Block":      r.get("block_index", "—"),
                            "Latency ms": r.get("latency_ms", "—"),
                            "Reason":     r.get("reason", ""),
                        })
                    st.dataframe(pd.DataFrame(df_rows), use_container_width=True)
                else:
                    st.error(f"Batch failed: {resp.text}")

    else:  # Verify batch
        st.markdown("Upload **multiple files** to verify all at once.")

        batch_ver_files = st.file_uploader(
            "Select files to verify",
            accept_multiple_files=True,
            key="batch_ver",
            label_visibility="collapsed",
        )

        if batch_ver_files:
            st.caption(f"{len(batch_ver_files)} file(s) selected")
            col_bvb, _ = st.columns([1, 3])
            with col_bvb:
                do_batch_ver = st.button("🔍 Verify All", key="btn_batch_ver")

            if do_batch_ver:
                with st.spinner("Verifying…"):
                    files_payload = [("files", (f.name, f.getvalue())) for f in batch_ver_files]
                    resp = api("post", "/verify/batch", files=files_payload)

                if resp is None:
                    st.error("Backend unreachable.")
                elif resp.ok:
                    data = resp.json()
                    results = data.get("results", [])
                    st.success(f"{len(results)} files verified")

                    verified = sum(1 for r in results if "VERIFIED" in r.get("status","").upper())
                    tampered = len(results) - verified
                    c1, c2 = st.columns(2)
                    c1.metric("✅ Verified", verified)
                    c2.metric("⚠️ Not Verified", tampered)

                    for r in results:
                        with st.expander(f"{file_type_icon(r.get('file_type',''))} {r.get('filename','file')} — {r.get('status','')}"):
                            show_verify_result(r)
                            lat = r.get("latency_ms")
                            if lat:
                                st.session_state.latencies.append(lat)
                else:
                    st.error(f"Batch verify failed: {resp.text}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 – LEDGER
# ══════════════════════════════════════════════════════════════════════════════
with tab_ledger:
    st.markdown("### 📘 Off-chain Trust Ledger")
    st.markdown("All registered documents with their issuers, hashes, and revocation status.")

    col_l1, col_l2 = st.columns([1, 4])
    with col_l1:
        load_ledger_btn = st.button("🔄 Load Ledger", key="btn_ledger")
    with col_l2:
        search_term = st.text_input("🔎 Filter by filename or issuer…", key="ledger_search", label_visibility="collapsed", placeholder="Filter by filename or issuer…")

    if load_ledger_btn:
        resp = api("get", "/ledger/view")
        if resp and resp.ok:
            records = resp.json().get("records", [])
            if records:
                df = pd.DataFrame(records)

                # Rename and select columns
                col_map = {
                    "filename":    "File",
                    "issuer_name": "Issuer",
                    "issuer_did":  "DID",
                    "file_type":   "Type",
                    "mime_type":   "MIME",
                    "size_bytes":  "Size (B)",
                    "signature_algo": "Algorithm",
                    "issued_at":   "Issued At",
                    "revoked":     "Revoked",
                    "hash":        "Hash (SHA-256)",
                }
                df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

                # Filter
                if search_term:
                    mask = df.apply(lambda col: col.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                    df = df[mask]

                st.dataframe(
                    df,
                    use_container_width=True,
                    height=400,
                )
                st.caption(f"{len(df)} record(s) shown")
            else:
                st.info("Ledger is empty — register some files first.")
        else:
            st.error("Failed to load ledger")

    # ─────────────────────────────────────────────────────────────────────────
    # 🗑️ Danger Zone – Clear Ledger
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div style="border:1px solid #7f1d1d;border-radius:10px;padding:1rem 1.2rem;background:rgba(127,29,29,0.08)">'
        '<span style="color:#f87171;font-weight:700;font-size:0.95rem">⚠️ Danger Zone</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    confirm_clear = st.checkbox(
        "I understand this will **permanently delete all ledger records** and cannot be undone.",
        key="confirm_clear",
    )

    col_clr, _ = st.columns([1, 4])
    with col_clr:
        clear_btn = st.button(
            "🗑️ Clear Entire Ledger",
            key="btn_clear_ledger",
            disabled=not confirm_clear,
        )

    if clear_btn and confirm_clear:
        resp = api("delete", "/ledger/clear")
        if resp is None:
            st.error("Backend unreachable.")
        elif resp.ok:
            result = resp.json()
            st.success(
                f"✅ Ledger cleared — **{result.get('records_removed', 0)}** record(s) deleted."
            )
            st.rerun()
        else:
            st.error(f"Failed to clear ledger: {resp.text}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 – BLOCKCHAIN
# ══════════════════════════════════════════════════════════════════════════════
with tab_blockchain:
    st.markdown("### ⛓️ Blockchain Explorer")
    st.markdown("Immutable proof-of-existence for every registered document.")

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        load_chain_btn = st.button("🔄 Load Blocks", key="btn_chain")
    with col_b2:
        health_btn = st.button("🩺 Chain Health Check", key="btn_chain_health")

    if health_btn:
        resp = api("get", "/blockchain/verify")
        if resp and resp.ok:
            valid = resp.json().get("blockchain_valid", False)
            if valid:
                st.success("✅ Blockchain is **intact** — all block hashes are valid")
            else:
                st.error("❌ Blockchain **compromised** — hash chain is broken!")

    if load_chain_btn:
        resp = api("get", "/blockchain/blocks")
        if resp and resp.ok:
            chain_data = resp.json()
            st.metric("Total Blocks", chain_data["total_blocks"])

            chain = chain_data["chain"]
            for block in reversed(chain):
                idx = block.get("index", 0)
                label = f"Block #{idx}" + (" — Genesis" if idx == 0 else f" | {block.get('issuer_did', '')}")
                with st.expander(label):
                    cols = st.columns(2)
                    cols[0].markdown(f"**Index:** `{block.get('index')}`")
                    if block.get("file_hash"):
                        cols[1].markdown(f"**File Hash:** `{block['file_hash'][:24]}…`")
                    if block.get("issuer_did"):
                        st.markdown(f"**Issuer:** `{block['issuer_did']}`")
                    st.markdown(f"**Block Hash:** `{block.get('block_hash','')[:32]}…`")
                    st.markdown(f"**Prev Hash:** `{block.get('previous_hash','')[:32]}…`")
                    import datetime
                    ts = datetime.datetime.fromtimestamp(block.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M:%S")
                    st.caption(f"🕐 {ts}")
        else:
            st.error("Failed to load blockchain")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 – ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
with tab_analytics:
    st.markdown("### 📊 Analytics & Monitoring")

    # ── Performance metrics
    col_m1, col_m2, col_m3 = st.columns(3)
    if st.session_state.latencies:
        avg = round(sum(st.session_state.latencies) / len(st.session_state.latencies), 2)
        col_m1.metric("Avg Latency (ms)", avg)
        col_m2.metric("Min Latency (ms)", round(min(st.session_state.latencies), 2))
        col_m3.metric("Total Operations", len(st.session_state.latencies))

        st.markdown("#### ⏱️ Verification Latency Over Time")
        lat_df = pd.DataFrame({"Latency (ms)": st.session_state.latencies})
        st.line_chart(lat_df)
    else:
        st.info("Perform some operations first to see analytics here.")

    st.divider()

    # ── Operation log
    if st.session_state.op_log:
        st.markdown("#### 📋 Operation Log (this session)")
        log_df = pd.DataFrame(st.session_state.op_log)
        log_df.columns = [c.title() for c in log_df.columns]
        st.dataframe(log_df, use_container_width=True)
        if st.button("🗑️ Clear Log"):
            st.session_state.op_log = []
            st.rerun()

    st.divider()

    # ── AI Anomaly Detection
    st.markdown("#### 🧠 AI Anomaly Detection")
    col_a1, col_a2 = st.columns([1, 3])
    with col_a1:
        if st.button("🔍 Run Detection", key="btn_anomaly"):
            with st.spinner("Analysing…"):
                resp = api("get", "/anomaly/check")
            if resp and resp.ok:
                st.json(resp.json())
            else:
                st.error("Anomaly check failed")

    st.markdown("#### 🤖 Autonomous Agent Action")
    col_ag1, col_ag2 = st.columns([1, 3])
    with col_ag1:
        if st.button("⚡ Trigger Agent", key="btn_agent"):
            with st.spinner("Running autonomous response…"):
                resp = api("post", "/agent/respond")
            if resp and resp.ok:
                st.json(resp.json())
            else:
                st.error("Agent call failed")


# ──────────────────────────────────────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#334155;font-size:0.78rem;padding:0.5rem 0">'
    '🛡️ Veracity Agent v2.0 &nbsp;|&nbsp; RSA-PSS-SHA256 &nbsp;|&nbsp; '
    'Blockchain Anchored &nbsp;|&nbsp; Multi-Issuer &nbsp;|&nbsp; AI Anomaly Detection'
    '</div>',
    unsafe_allow_html=True,
)
