"""
app.py — LexAI Streamlit Frontend
Run: streamlit run app.py
Make sure FastAPI backend is running on http://127.0.0.1:8000
"""

import streamlit as st
import requests
import json
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LexAI — Legal Statute Identification System",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://127.0.0.1:8000"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Serif+4:wght@300;400;600&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Source Serif 4', Georgia, serif !important;
}
.stApp {
    background: #0a0c0f;
    color: #d4c9b0;
}

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d0f13 !important;
    border-right: 1px solid #c9a84c22 !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #9a9080 !important;
    font-family: 'Source Serif 4', serif !important;
    font-size: 0.9rem !important;
    padding: 4px 0 !important;
}
[data-testid="stSidebar"] .stRadio label:hover { color: #c9a84c !important; }

/* Header */
.lex-header {
    background: linear-gradient(135deg, #0d1117, #111620);
    border: 1px solid #c9a84c22;
    border-radius: 8px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.lex-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 2rem !important;
    color: #c9a84c !important;
    letter-spacing: 4px;
    margin: 0 !important;
}
.lex-subtitle {
    color: #5a5040;
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.lex-badge {
    background: #1a1710;
    border: 1px solid #c9a84c44;
    color: #c9a84c;
    font-size: 0.65rem;
    letter-spacing: 2px;
    padding: 4px 12px;
    border-radius: 2px;
    text-transform: uppercase;
    display: inline-block;
    margin-top: 6px;
}

/* Cards */
.result-card {
    background: #111318;
    border: 1px solid #c9a84c22;
    border-radius: 6px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.result-card-title {
    font-family: 'Playfair Display', serif;
    color: #c9a84c;
    font-size: 0.8rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
    border-bottom: 1px solid #c9a84c22;
    padding-bottom: 0.5rem;
}

/* Section pills */
.section-pill {
    display: inline-block;
    background: #1a1710;
    border: 1px solid #c9a84c44;
    color: #c9a84c;
    padding: 4px 12px;
    border-radius: 3px;
    font-size: 0.78rem;
    margin: 3px;
    letter-spacing: 0.5px;
}
.section-nb {
    border-color: #aa4444;
    color: #cc6666;
    background: #1a0e0e;
}

/* Risk badges */
.risk-high   { color: #ff6b6b; background: #1a0e0e; border: 1px solid #aa4444; padding: 4px 14px; border-radius: 3px; font-size: 0.85rem; font-weight: 600; }
.risk-medium { color: #ffcc55; background: #1a1608; border: 1px solid #aa8822; padding: 4px 14px; border-radius: 3px; font-size: 0.85rem; font-weight: 600; }
.risk-low    { color: #66bb88; background: #0e1a12; border: 1px solid #336644; padding: 4px 14px; border-radius: 3px; font-size: 0.85rem; font-weight: 600; }

/* Fault badges */
.fault-victim   { color: #66bb88; background: #0e1a12; border: 1px solid #336644; padding: 4px 14px; border-radius: 3px; }
.fault-accused  { color: #ff6b6b; background: #1a0e0e; border: 1px solid #aa4444; padding: 4px 14px; border-radius: 3px; }
.fault-both     { color: #ffcc55; background: #1a1608; border: 1px solid #aa8822; padding: 4px 14px; border-radius: 3px; }
.fault-unclear  { color: #9a9080; background: #111318; border: 1px solid #333; padding: 4px 14px; border-radius: 3px; }

/* Text area */
.stTextArea textarea {
    background: #0f1115 !important;
    border: 1px solid #c9a84c33 !important;
    color: #ccc4aa !important;
    font-family: 'Source Serif 4', serif !important;
    font-size: 0.9rem !important;
    border-radius: 6px !important;
}
.stTextArea textarea:focus {
    border-color: #c9a84c88 !important;
    box-shadow: none !important;
}

/* Text inputs */
.stTextInput input {
    background: #0f1115 !important;
    border: 1px solid #c9a84c22 !important;
    color: #ccc4aa !important;
    font-family: 'Source Serif 4', serif !important;
    border-radius: 4px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #c9a84c, #b8943c) !important;
    color: #0a0c0f !important;
    border: none !important;
    font-family: 'Source Serif 4', serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 2px !important;
    font-weight: 600 !important;
    padding: 0.6rem 2rem !important;
    border-radius: 4px !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #d4b86a, #c9a84c) !important;
    transform: translateY(-1px) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: #111318 !important;
    border: 1px solid #c9a84c22 !important;
    color: #c9a84c !important;
    font-family: 'Source Serif 4', serif !important;
    border-radius: 4px !important;
}

/* Draft output */
.draft-output {
    background: #080a0d;
    border: 1px solid #c9a84c22;
    border-left: 3px solid #c9a84c;
    border-radius: 0 6px 6px 0;
    padding: 1.5rem;
    font-family: 'Courier New', monospace;
    font-size: 0.78rem;
    color: #b0a890;
    white-space: pre-wrap;
    line-height: 1.7;
    max-height: 500px;
    overflow-y: auto;
}

/* Metric cards */
.metric-box {
    background: #111318;
    border: 1px solid #c9a84c22;
    border-radius: 6px;
    padding: 1rem;
    text-align: center;
}
.metric-val {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    color: #c9a84c;
}
.metric-label {
    font-size: 0.7rem;
    color: #5a5040;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* Disclaimer */
.disclaimer {
    background: #0c0e12;
    border: 1px solid #333;
    border-radius: 4px;
    padding: 10px 16px;
    font-size: 0.72rem;
    color: #3a3530;
    margin-top: 1rem;
    text-align: center;
}

/* Landmark case */
.landmark {
    border-left: 3px solid #c9a84c44;
    padding: 8px 12px;
    margin: 6px 0;
    background: #0e1015;
    border-radius: 0 4px 4px 0;
}
.landmark-name { color: #c9a84c; font-size: 0.85rem; font-weight: 600; }
.landmark-court { color: #5a5040; font-size: 0.72rem; }
.landmark-rel { color: #9a9080; font-size: 0.78rem; margin-top: 4px; }

/* Step item */
.step-item {
    padding: 6px 0;
    color: #9a9080;
    font-size: 0.85rem;
    border-bottom: 1px solid #1a1a1e;
}
.step-item:last-child { border-bottom: none; }
</style>
""", unsafe_allow_html=True)


# ── API helpers ───────────────────────────────────────────────────────────────
def api_get(endpoint):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def api_post(endpoint, payload):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=15)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="lex-header">
    <div style="font-size:2.5rem">⚖</div>
    <div>
        <div class="lex-title">LEXAI</div>
        <div class="lex-subtitle">AI Legal Statute Identification System · Indian Law</div>
        <div class="lex-badge">LeSICiN Dataset · IIT Kharagpur · AAAI-22 · Zenodo 6053791</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Backend status check ──────────────────────────────────────────────────────
health = api_get("/health")
if not health:
    st.error("⚠ Backend server is not running. Start it with: `uvicorn main:app --reload --app-dir src`")
    st.stop()

model_info = api_get("/model/info") or {}
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-box"><div class="metric-val">⚖</div><div class="metric-label">System Active</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-box"><div class="metric-val" style="font-size:1.1rem">{model_info.get("active_model","—")}</div><div class="metric-label">Active Model</div></div>', unsafe_allow_html=True)
with col3:
    secs = api_get("/sections")
    count = secs["total"] if secs else "38"
    st.markdown(f'<div class="metric-box"><div class="metric-val">{count}</div><div class="metric-label">IPC Sections</div></div>', unsafe_allow_html=True)
with col4:
    cats = api_get("/categories")
    ccount = cats["total"] if cats else "13"
    st.markdown(f'<div class="metric-box"><div class="metric-val">{ccount}</div><div class="metric-label">Legal Categories</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="font-family:'Playfair Display',serif; color:#c9a84c; font-size:1.1rem; letter-spacing:3px; margin-bottom:1.5rem; padding-bottom:0.5rem; border-bottom:1px solid #c9a84c22;">
⚖ LEXAI
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div style="color:#5a5040;font-size:0.65rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.5rem;">Navigation</div>', unsafe_allow_html=True)

page = st.sidebar.radio("", [
    "⚖  Case Analysis",
    "📋  Draft FIR",
    "📜  Legal Notice",
    "🔓  Bail Application",
    "📁  Document Checklist",
    "📚  IPC Sections",
    "📊  Model Evaluation",
], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="font-size:0.65rem; color:#3a3530; line-height:1.6;">
⚠ This system provides AI-generated legal information only. It does not constitute legal advice. Consult a qualified advocate for legal proceedings.
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: CASE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
if "Case Analysis" in page:
    st.markdown('<div class="result-card-title" style="font-size:1rem;letter-spacing:3px;">⚖ CASE ANALYSIS</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#5a5040;font-size:0.8rem;margin-bottom:1rem;">Describe your legal situation in detail. The AI will identify applicable IPC sections, determine fault, assess risk, and provide recommendations.</div>', unsafe_allow_html=True)

    description = st.text_area(
        "Case Description",
        placeholder="Example: Someone hacked my bank account and transferred Rs 50,000 without my knowledge. They also sent me threatening messages on WhatsApp...",
        height=150,
        label_visibility="collapsed",
    )

    col_btn, col_ex = st.columns([1, 3])
    with col_btn:
        analyze_btn = st.button("ANALYZE CASE", use_container_width=True)
    with col_ex:
        if st.button("Load Example", use_container_width=False):
            st.session_state["example_loaded"] = True

    if st.session_state.get("example_loaded"):
        description = "My neighbour broke into my house last night and stole gold jewellery worth Rs 2 lakh and cash of Rs 50,000. He also threatened to kill me if I complained to police."
        st.session_state["example_loaded"] = False
        st.rerun()

    if analyze_btn and description.strip():
        with st.spinner("Analyzing case..."):
            result, status = api_post("/analyze", {"description": description})

        if status != 200:
            st.error(f"Error: {result.get('detail', 'Unknown error')}")
        else:
            # ── Sections ──────────────────────────────────────────────────────
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div class="result-card-title">SECTIONS IDENTIFIED</div>', unsafe_allow_html=True)
            sections = result.get("sections_identified", [])
            if sections:
                pills = ""
                for s in sections:
                    cls = "section-pill section-nb" if not s.get("bailable") else "section-pill"
                    conf = f" ({s.get('confidence',0):.0f}%)" if s.get("confidence") else ""
                    pills += f'<span class="{cls}">{s["section"]}{conf}</span>'
                st.markdown(pills, unsafe_allow_html=True)
                st.markdown(f'<div style="color:#5a5040;font-size:0.72rem;margin-top:8px;">🔴 Red = Non-Bailable &nbsp;|&nbsp; Model: {result.get("model_used","rule-based")}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#5a5040;">No specific sections matched. Provide more details.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Fault + Risk side by side ─────────────────────────────────────
            col_f, col_r = st.columns(2)
            with col_f:
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown('<div class="result-card-title">FAULT ANALYSIS</div>', unsafe_allow_html=True)
                fault = result.get("fault_status", "UNCLEAR")
                fault_cls = {"VICTIM":"fault-victim","AT_FAULT":"fault-accused","BOTH":"fault-both"}.get(fault,"fault-unclear")
                fault_label = {"VICTIM":"✓ VICTIM","AT_FAULT":"⚠ ACCUSED","BOTH":"⚡ BOTH PARTIES","UNCLEAR":"? UNCLEAR"}.get(fault, fault)
                st.markdown(f'<span class="{fault_cls}">{fault_label}</span>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#9a9080;font-size:0.8rem;margin-top:10px;">{result.get("fault_analysis","")}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_r:
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown('<div class="result-card-title">RISK ASSESSMENT</div>', unsafe_allow_html=True)
                risk = result.get("risk_assessment", {})
                rl   = risk.get("level","UNKNOWN")
                risk_cls = {"HIGH":"risk-high","MEDIUM":"risk-medium","LOW":"risk-low"}.get(rl,"")
                st.markdown(f'<span class="{risk_cls}">{risk.get("icon","")} {rl}</span>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#9a9080;font-size:0.78rem;margin-top:8px;">{risk.get("description","")}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#5a5040;font-size:0.72rem;margin-top:6px;">🔒 {risk.get("bail_type","")}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Section details ───────────────────────────────────────────────
            if sections:
                with st.expander(f"📋 View Detailed Section Information ({len(sections)} sections)"):
                    for s in sections:
                        b_label = "✅ Bailable" if s.get("bailable") else "🔴 Non-Bailable"
                        c_label = "Cognizable" if s.get("cognizable") else "Non-Cognizable"
                        st.markdown(f"""
<div style="background:#0e1015;border:1px solid #c9a84c22;border-radius:4px;padding:1rem;margin-bottom:0.8rem;">
  <div style="color:#c9a84c;font-size:0.9rem;font-weight:600;">{s['section']} — {s['title']}</div>
  <div style="color:#7a7060;font-size:0.78rem;margin:4px 0;">{s.get('description','')}</div>
  <div style="color:#9a9080;font-size:0.78rem;">⚖ <b>Punishment:</b> {s.get('punishment','')}</div>
  <div style="margin-top:6px;">
    <span style="background:#1a1710;border:1px solid #c9a84c33;color:#c9a84c;padding:2px 8px;border-radius:2px;font-size:0.68rem;">{b_label}</span>
    <span style="background:#111318;border:1px solid #333;color:#6a6050;padding:2px 8px;border-radius:2px;font-size:0.68rem;margin-left:4px;">{c_label}</span>
    <span style="background:#111318;border:1px solid #333;color:#6a6050;padding:2px 8px;border-radius:2px;font-size:0.68rem;margin-left:4px;">🏛 {s.get('court','')}</span>
  </div>
</div>
""", unsafe_allow_html=True)

            # ── Recommendations ───────────────────────────────────────────────
            with st.expander("💡 Smart Recommendations"):
                for rec in result.get("recommendations", []):
                    st.markdown(f'<div class="step-item">{rec}</div>', unsafe_allow_html=True)

            # ── Rights ────────────────────────────────────────────────────────
            with st.expander("🛡 Your Legal Rights"):
                for right in result.get("your_rights", []):
                    st.markdown(f'<div class="step-item">• {right}</div>', unsafe_allow_html=True)

            # ── Next Steps ────────────────────────────────────────────────────
            with st.expander("📌 Next Steps"):
                for step in result.get("next_steps", []):
                    st.markdown(f'<div class="step-item">{step}</div>', unsafe_allow_html=True)

            # ── Landmark Cases ────────────────────────────────────────────────
            landmarks = result.get("landmark_cases", [])
            if landmarks and landmarks[0].get("case") != "No specific landmark cases found":
                with st.expander(f"📚 Landmark Cases ({len(landmarks)})"):
                    for lc in landmarks:
                        st.markdown(f"""
<div class="landmark">
  <div class="landmark-name">{lc['case']}</div>
  <div class="landmark-court">{lc['court']}</div>
  <div class="landmark-rel">{lc['relevance']}</div>
</div>""", unsafe_allow_html=True)

            # ── Document checklist ────────────────────────────────────────────
            checklist = result.get("document_checklist", {})
            if checklist:
                with st.expander("📁 Document Checklist"):
                    docs = checklist.get("category_specific", []) + checklist.get("always_required", [])
                    for d in docs:
                        st.markdown(f'<div class="step-item">📄 {d}</div>', unsafe_allow_html=True)

            st.markdown('<div class="disclaimer">⚠ AI-generated legal information only. Not a substitute for professional legal advice from a qualified advocate.</div>', unsafe_allow_html=True)

    elif analyze_btn:
        st.warning("Please enter a case description.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DRAFT FIR
# ═══════════════════════════════════════════════════════════════════════════════
elif "Draft FIR" in page:
    st.markdown('<div class="result-card-title" style="font-size:1rem;letter-spacing:3px;">📋 DRAFT FIRST INFORMATION REPORT</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#5a5040;font-size:0.8rem;margin-bottom:1.5rem;">Fill in the details below to generate a formal FIR under Section 154 CrPC.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        complainant = st.text_input("Complainant Name *", placeholder="Full name")
        age         = st.text_input("Age *", placeholder="e.g. 28")
        address     = st.text_input("Address *", placeholder="Full address with PIN code")
        police_stn  = st.text_input("Police Station *", placeholder="e.g. Connaught Place Police Station")
    with col2:
        accused     = st.text_input("Accused Name", placeholder="Name or 'Unknown person'")
        witnesses   = st.text_input("Witnesses", placeholder="Names of witnesses if any")
        inc_date    = st.text_input("Date & Time of Incident *", placeholder="e.g. 10 January 2025, 11:00 PM")
        inc_loc     = st.text_input("Location of Incident *", placeholder="Exact location")

    sections_input = st.text_input("Applicable Sections (comma separated)", placeholder="e.g. Section 379 IPC, Section 506 IPC")
    inc_desc = st.text_area("Incident Description *", placeholder="Describe what happened in detail...", height=120)

    if st.button("GENERATE FIR DRAFT", use_container_width=False):
        if complainant and inc_desc and police_stn:
            sections_list = [s.strip() for s in sections_input.split(",") if s.strip()] if sections_input else []
            payload = {
                "complainant_name": complainant, "age": age, "address": address,
                "incident_description": inc_desc, "incident_date": inc_date,
                "incident_location": inc_loc, "accused_name": accused or "Unknown",
                "witnesses": witnesses or "None", "police_station": police_stn,
                "sections": sections_list,
            }
            with st.spinner("Generating FIR..."):
                result, status = api_post("/draft/fir", payload)
            if status == 200:
                st.success("✓ FIR Draft Generated")
                st.markdown('<div class="draft-output">' + result["fir_draft"].replace("\n", "<br>") + '</div>', unsafe_allow_html=True)
                st.download_button("⬇ Download FIR Draft", result["fir_draft"], file_name=f"FIR_Draft_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain")
            else:
                st.error(f"Error: {result.get('detail','Unknown error')}")
        else:
            st.warning("Please fill in all required fields (*).")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: LEGAL NOTICE
# ═══════════════════════════════════════════════════════════════════════════════
elif "Legal Notice" in page:
    st.markdown('<div class="result-card-title" style="font-size:1rem;letter-spacing:3px;">📜 DRAFT LEGAL NOTICE</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#5a5040;font-size:0.8rem;margin-bottom:1.5rem;">Generate a formal legal notice to be sent through an advocate.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        sender_name    = st.text_input("Your Name (Sender) *")
        sender_address = st.text_input("Your Address *")
        subject        = st.text_input("Subject / Title *", placeholder="e.g. Deficiency in Service")
        deadline       = st.text_input("Response Deadline (days)", value="15")
    with col2:
        receiver_name    = st.text_input("Receiver Name *")
        receiver_address = st.text_input("Receiver Address *")
        sections_input   = st.text_input("Applicable Sections", placeholder="e.g. Consumer Protection Act 2019")

    facts  = st.text_area("Facts of the Matter *", placeholder="Describe what happened...", height=100)
    demand = st.text_area("Your Demand *", placeholder="What are you demanding? e.g. Refund of Rs 50,000 within 15 days", height=80)

    if st.button("GENERATE LEGAL NOTICE", use_container_width=False):
        if sender_name and receiver_name and facts and demand:
            sections_list = [s.strip() for s in sections_input.split(",") if s.strip()] if sections_input else []
            payload = {
                "sender_name": sender_name, "sender_address": sender_address,
                "receiver_name": receiver_name, "receiver_address": receiver_address,
                "subject": subject, "facts": facts, "demand": demand,
                "deadline_days": deadline, "sections": sections_list,
            }
            with st.spinner("Generating Legal Notice..."):
                result, status = api_post("/draft/legal-notice", payload)
            if status == 200:
                st.success("✓ Legal Notice Generated")
                st.markdown('<div class="draft-output">' + result["notice_draft"].replace("\n", "<br>") + '</div>', unsafe_allow_html=True)
                st.download_button("⬇ Download Legal Notice", result["notice_draft"], file_name=f"Legal_Notice_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain")
            else:
                st.error(f"Error: {result.get('detail','Unknown error')}")
        else:
            st.warning("Please fill in all required fields (*).")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: BAIL APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════
elif "Bail Application" in page:
    st.markdown('<div class="result-card-title" style="font-size:1rem;letter-spacing:3px;">🔓 DRAFT BAIL APPLICATION</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#5a5040;font-size:0.8rem;margin-bottom:1.5rem;">Generate a bail application draft under Section 437 / 438 / 439 CrPC.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        accused_name = st.text_input("Accused Name *")
        age          = st.text_input("Age *")
        address      = st.text_input("Address *")
    with col2:
        fir_no    = st.text_input("FIR Number *", placeholder="e.g. 123/2025")
        police_stn= st.text_input("Police Station *")
        sections_input = st.text_input("Sections", placeholder="e.g. Section 420 IPC")

    grounds = st.text_area("Grounds for Bail *",
        value="The accused has no prior criminal record and undertakes to cooperate fully with the investigation and appear before the court as and when required.",
        height=100)

    if st.button("GENERATE BAIL APPLICATION", use_container_width=False):
        if accused_name and fir_no and police_stn:
            sections_list = [s.strip() for s in sections_input.split(",") if s.strip()] if sections_input else []
            payload = {
                "accused_name": accused_name, "age": age, "address": address,
                "fir_number": fir_no, "police_station": police_stn,
                "sections": sections_list, "grounds": grounds,
            }
            with st.spinner("Generating Bail Application..."):
                result, status = api_post("/draft/bail-application", payload)
            if status == 200:
                st.success("✓ Bail Application Generated")
                st.markdown('<div class="draft-output">' + result["bail_application_draft"].replace("\n", "<br>") + '</div>', unsafe_allow_html=True)
                st.download_button("⬇ Download Bail Application", result["bail_application_draft"], file_name=f"Bail_Application_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain")
            else:
                st.error(f"Error: {result.get('detail','Unknown error')}")
        else:
            st.warning("Please fill in all required fields (*).")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DOCUMENT CHECKLIST
# ═══════════════════════════════════════════════════════════════════════════════
elif "Document Checklist" in page:
    st.markdown('<div class="result-card-title" style="font-size:1rem;letter-spacing:3px;">📁 DOCUMENT CHECKLIST</div>', unsafe_allow_html=True)

    cats_data = api_get("/categories")
    cats = cats_data["categories"] if cats_data else ["Cyber Crime","Fraud & Cheating","Offences Against Women","Offences Against Body","Property Offences","Motor Vehicle","Consumer Protection","Corruption"]

    selected_cat = st.selectbox("Select Legal Category", cats)

    if st.button("GET CHECKLIST", use_container_width=False):
        result, status = api_post("/checklist", {"category": selected_cat})
        if status == 200:
            st.markdown(f'<div class="result-card-title" style="margin-top:1rem;">Documents Required for: {selected_cat}</div>', unsafe_allow_html=True)
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div style="color:#c9a84c;font-size:0.75rem;letter-spacing:2px;margin-bottom:0.5rem;">CATEGORY-SPECIFIC DOCUMENTS</div>', unsafe_allow_html=True)
            for d in result.get("documents", []):
                st.markdown(f'<div class="step-item">📄 {d}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div style="color:#c9a84c;font-size:0.75rem;letter-spacing:2px;margin-bottom:0.5rem;">ALWAYS REQUIRED</div>', unsafe_allow_html=True)
            for d in result.get("always_required", []):
                st.markdown(f'<div class="step-item">📄 {d}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: IPC SECTIONS
# ═══════════════════════════════════════════════════════════════════════════════
elif "IPC Sections" in page:
    st.markdown('<div class="result-card-title" style="font-size:1rem;letter-spacing:3px;">📚 IPC SECTIONS KNOWLEDGE BASE</div>', unsafe_allow_html=True)

    data = api_get("/sections")
    if data:
        cats_data = api_get("/categories")
        cats = ["All"] + (cats_data["categories"] if cats_data else [])
        filter_cat = st.selectbox("Filter by Category", cats)

        sections = data["sections"]
        if filter_cat != "All":
            sections = [s for s in sections if s["category"] == filter_cat]

        st.markdown(f'<div style="color:#5a5040;font-size:0.75rem;margin-bottom:1rem;">{len(sections)} sections found</div>', unsafe_allow_html=True)

        for s in sections:
            b = "✅ Bailable" if s["bailable"] else "🔴 Non-Bailable"
            c = "Cognizable" if s["cognizable"] else "Non-Cognizable"
            st.markdown(f"""
<div style="background:#111318;border:1px solid #c9a84c22;border-radius:4px;padding:1rem;margin-bottom:0.5rem;">
  <div style="display:flex;justify-content:space-between;align-items:start;">
    <div>
      <span style="color:#c9a84c;font-size:0.9rem;font-weight:600;">{s['section']}</span>
      <span style="color:#7a7060;font-size:0.8rem;margin-left:10px;">— {s['title']}</span>
    </div>
    <span style="color:#5a5040;font-size:0.7rem;letter-spacing:1px;">{s['category']}</span>
  </div>
  <div style="color:#9a9080;font-size:0.78rem;margin-top:6px;">⚖ {s['punishment']}</div>
  <div style="margin-top:6px;">
    <span style="background:#1a1710;border:1px solid #c9a84c33;color:#c9a84c;padding:2px 8px;border-radius:2px;font-size:0.65rem;">{b}</span>
    <span style="background:#111318;border:1px solid #333;color:#6a6050;padding:2px 8px;border-radius:2px;font-size:0.65rem;margin-left:4px;">{c}</span>
  </div>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: MODEL EVALUATION
# ═══════════════════════════════════════════════════════════════════════════════
elif "Evaluation" in page:
    st.markdown('<div class="result-card-title" style="font-size:1rem;letter-spacing:3px;">📊 MODEL EVALUATION RESULTS</div>', unsafe_allow_html=True)

    data = api_get("/evaluation")
    if data and "message" not in data:
        st.markdown(f'<div style="color:#5a5040;font-size:0.78rem;margin-bottom:1rem;">Dataset: {data.get("dataset","")} | Generated: {data.get("generated_at","")}</div>', unsafe_allow_html=True)

        for model_key, res in data.get("results", {}).items():
            test = res.get("test", {})
            st.markdown(f'<div class="result-card-title" style="margin-top:1rem;">{res.get("model","")}</div>', unsafe_allow_html=True)
            c1,c2,c3,c4,c5 = st.columns(5)
            metrics = [
                ("F1-Micro",    test.get("f1_micro",0)),
                ("F1-Macro",    test.get("f1_macro",0)),
                ("Precision",   test.get("precision",0)),
                ("Recall",      test.get("recall",0)),
                ("Hamming Loss",test.get("hamming_loss",0)),
            ]
            for col, (label, val) in zip([c1,c2,c3,c4,c5], metrics):
                with col:
                    st.markdown(f'<div class="metric-box"><div class="metric-val">{val:.3f}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown("""
<div class="result-card">
<div style="color:#c9a84c;margin-bottom:1rem;">No evaluation results yet.</div>
<div style="color:#9a9080;font-size:0.85rem;line-height:1.8;">
To train the model and generate evaluation metrics:<br><br>
<b>Step 1:</b> Download dataset from <a href="https://zenodo.org/records/6053791" style="color:#c9a84c;">zenodo.org/records/6053791</a><br>
<b>Step 2:</b> Place files in the <code>datasets/</code> folder<br>
<b>Step 3:</b> Run: <code>python src/trainer.py --model tfidf</code><br>
<b>Step 4:</b> Refresh this page
</div>
</div>""", unsafe_allow_html=True)

        st.markdown('<div style="color:#5a5040;font-size:0.78rem;margin-top:1rem;">Expected results after training (based on LeSICiN paper):</div>', unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        expected = [("F1-Micro","~0.81"),("F1-Macro","~0.61"),("Precision","~0.83"),("Recall","~0.79")]
        for col,(label,val) in zip([c1,c2,c3,c4], expected):
            with col:
                st.markdown(f'<div class="metric-box"><div class="metric-val" style="font-size:1.4rem;">{val}</div><div class="metric-label">{label}<br>(InLegalBERT)</div></div>', unsafe_allow_html=True)
