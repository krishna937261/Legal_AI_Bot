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

API_BASE = https://legal-ai-bot-w8ro.onrender.com

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
    "🏛  RTI Assistant",
    "🚗  Traffic Fine Checker",
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


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: RTI ASSISTANT
# ═══════════════════════════════════════════════════════════════════════════════
elif "RTI Assistant" in page:
    st.markdown('<div class="result-card-title" style="font-size:1rem;letter-spacing:3px;">🏛 RTI APPLICATION ASSISTANT</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#5a5040;font-size:0.8rem;margin-bottom:1.5rem;">Draft a Right to Information application under the RTI Act, 2005. Identify the correct public authority and frame your query effectively.</div>', unsafe_allow_html=True)

    # ── Authority selector ────────────────────────────────────────────────────
    AUTHORITIES = {
        "Central Government": [
            "Ministry of Finance", "Ministry of Home Affairs", "Ministry of Law & Justice",
            "Ministry of Education", "Ministry of Health & Family Welfare",
            "Ministry of Railways", "Ministry of External Affairs",
            "Ministry of Defence", "Income Tax Department", "Central Bureau of Investigation (CBI)",
            "Enforcement Directorate (ED)", "SEBI", "RBI", "EPFO",
        ],
        "State Government": [
            "State Police Department", "State Revenue Department", "State PWD",
            "State Health Department", "State Education Department",
            "State Electricity Board", "Municipal Corporation", "Gram Panchayat",
            "District Collectorate", "State Transport Department",
        ],
        "Judiciary & Constitutional Bodies": [
            "High Court Registry", "Supreme Court Registry",
            "Election Commission of India", "CAG Office", "UPSC", "State PSC",
        ],
        "Public Sector Undertakings": [
            "BSNL", "ONGC", "BHEL", "Air India", "Indian Oil Corporation",
            "NTPC", "Coal India", "LIC of India", "SBI", "Bank of Baroda",
        ],
    }

    col1, col2 = st.columns(2)
    with col1:
        authority_type = st.selectbox("Type of Public Authority *", list(AUTHORITIES.keys()))
        authority_name = st.selectbox("Select Authority *", AUTHORITIES[authority_type])
        applicant_name = st.text_input("Your Full Name *", placeholder="As per Aadhaar / PAN")
        applicant_address = st.text_input("Your Address *", placeholder="Full address with PIN code")
    with col2:
        applicant_phone = st.text_input("Mobile Number", placeholder="10-digit mobile number")
        applicant_email = st.text_input("Email Address", placeholder="your@email.com")
        rti_fee_paid = st.selectbox("RTI Fee Payment Mode", ["Indian Postal Order (IPO)", "Demand Draft", "Online Payment", "Court Fee Stamp"])
        state = st.text_input("State", placeholder="e.g. Maharashtra, Delhi")

    subject = st.text_input("Subject of RTI Application *", placeholder="e.g. Status of my pending PF withdrawal claim")
    info_sought = st.text_area(
        "Information Sought *",
        placeholder="Describe clearly what information you want. Be specific.\ne.g. Please provide:\n1. Current status of my PF withdrawal application no. XXXX\n2. Dates of all actions taken on my application\n3. Name and designation of the officer handling my case",
        height=150
    )
    period = st.text_input("Period of Information", placeholder="e.g. From January 2023 to December 2024")

    if st.button("GENERATE RTI APPLICATION", use_container_width=False):
        if applicant_name and applicant_address and subject and info_sought:
            from datetime import date
            today = date.today().strftime("%d %B %Y")
            rti_draft = f"""TO,
The Public Information Officer (PIO),
{authority_name},
{authority_type},
{state if state else '[State]'}

Date: {today}

SUBJECT: APPLICATION UNDER RIGHT TO INFORMATION ACT, 2005 — {subject.upper()}

Sir/Madam,

I, {applicant_name}, resident of {applicant_address}, hereby request the following information under Section 6(1) of the Right to Information Act, 2005:

INFORMATION SOUGHT:
{info_sought}

{"PERIOD: " + period if period else ""}

I am enclosing the application fee of Rs. 10/- by way of {rti_fee_paid} as required under the RTI Act, 2005.

If the information sought is held by another public authority or the subject matter more closely concerns another public authority, I request you to transfer this application under Section 6(3) of the RTI Act, 2005.

I request you to provide the information within the stipulated period of 30 days as prescribed under Section 7(1) of the RTI Act, 2005.

Thanking you,

Yours faithfully,

{applicant_name}
Address: {applicant_address}
{("Mobile: " + applicant_phone) if applicant_phone else ""}
{("Email: " + applicant_email) if applicant_email else ""}
Date: {today}

——————————————————————————————————
IMPORTANT NOTES:
• Send via Speed Post / Registered Post and keep acknowledgement.
• If no reply within 30 days, file First Appeal under Section 19(1) with the Appellate Authority.
• If First Appeal unsatisfactory, file Second Appeal with Central/State Information Commission within 90 days.
• RTI fee: Rs. 10/- (free for BPL applicants — attach BPL card copy).
• You may track your RTI at: rtionline.gov.in (for Central Government RTIs)
——————————————————————————————————"""

            st.success("✓ RTI Application Generated")
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div class="result-card-title">RTI APPLICATION DRAFT</div>', unsafe_allow_html=True)
            st.markdown('<div class="draft-output">' + rti_draft.replace("\n", "<br>") + '</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.download_button(
                "⬇ Download RTI Application",
                rti_draft,
                file_name=f"RTI_Application_{applicant_name.replace(' ','_')}_{today.replace(' ','_')}.txt",
                mime="text/plain"
            )

            # Tips
            st.markdown('<div class="result-card" style="margin-top:1rem;">', unsafe_allow_html=True)
            st.markdown('<div class="result-card-title">📌 TIPS FOR BEST RESPONSE</div>', unsafe_allow_html=True)
            tips = [
                "Be specific — vague questions get vague answers.",
                "Ask for documents/records, not opinions or explanations.",
                "Use numbered points to list each piece of information separately.",
                "If denied, cite Section 19(1) in your First Appeal.",
                "Keep a copy of everything you send and receive.",
                "Central RTIs can be filed online at rtionline.gov.in",
            ]
            for tip in tips:
                st.markdown(f'<div class="step-item">💡 {tip}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="disclaimer">⚠ This is an AI-generated RTI draft. Review before sending. For complex matters, consult a legal expert or RTI activist.</div>', unsafe_allow_html=True)
        else:
            st.warning("Please fill in all required fields (*).")

    # ── RTI Info ──────────────────────────────────────────────────────────────
    with st.expander("📖 What is RTI? Know Your Rights"):
        st.markdown("""
<div style="color:#9a9080;font-size:0.85rem;line-height:2;">
<span style="color:#c9a84c;font-weight:600;">Right to Information Act, 2005</span> gives every Indian citizen the right to request information from any public authority.<br><br>
<span style="color:#c9a84c;">Who can apply?</span> Any Indian citizen.<br>
<span style="color:#c9a84c;">Fee:</span> Rs. 10/- (Free for BPL cardholders).<br>
<span style="color:#c9a84c;">Response time:</span> 30 days (48 hours if life/liberty at stake).<br>
<span style="color:#c9a84c;">First Appeal:</span> Within 30 days of no/unsatisfactory reply — to Appellate Authority.<br>
<span style="color:#c9a84c;">Second Appeal:</span> Within 90 days — to Central/State Information Commission.<br>
<span style="color:#c9a84c;">Online portal:</span> rtionline.gov.in (for Central Government departments).<br>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: TRAFFIC FINE CHECKER
# ═══════════════════════════════════════════════════════════════════════════════
elif "Traffic Fine Checker" in page:
    st.markdown('<div class="result-card-title" style="font-size:1rem;letter-spacing:3px;">🚗 TRAFFIC FINE CHECKER</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#5a5040;font-size:0.8rem;margin-bottom:1.5rem;">Instant look-up of fines under the Motor Vehicles (Amendment) Act, 2019. Search by offence or browse by category.</div>', unsafe_allow_html=True)

    FINES_DB = [
        {"offence": "Drunken Driving", "category": "Impairment", "section": "Sec 185 MVA", "first_offence": "₹10,000 or 6 months imprisonment or both", "repeat_offence": "₹15,000 or 2 years imprisonment or both", "severity": "HIGH"},
        {"offence": "Over Speeding (LMV)", "category": "Speed", "section": "Sec 183 MVA", "first_offence": "₹1,000", "repeat_offence": "₹2,000", "severity": "MEDIUM"},
        {"offence": "Over Speeding (Medium Passenger Vehicle)", "category": "Speed", "section": "Sec 183 MVA", "first_offence": "₹2,000", "repeat_offence": "₹4,000", "severity": "MEDIUM"},
        {"offence": "Driving Without Licence", "category": "Licence", "section": "Sec 181 MVA", "first_offence": "₹5,000", "repeat_offence": "₹10,000", "severity": "HIGH"},
        {"offence": "Driving Despite Disqualification", "category": "Licence", "section": "Sec 182 MVA", "first_offence": "₹10,000 or 3 months imprisonment or both", "repeat_offence": "₹10,000 or 3 months imprisonment or both", "severity": "HIGH"},
        {"offence": "Not Wearing Helmet", "category": "Safety Gear", "section": "Sec 194D MVA", "first_offence": "₹1,000 + 3 months disqualification", "repeat_offence": "₹2,000 + 3 months disqualification", "severity": "MEDIUM"},
        {"offence": "Not Wearing Seat Belt", "category": "Safety Gear", "section": "Sec 194B MVA", "first_offence": "₹1,000", "repeat_offence": "₹1,000", "severity": "LOW"},
        {"offence": "Using Mobile Phone While Driving", "category": "Distraction", "section": "Sec 184 MVA", "first_offence": "₹5,000", "repeat_offence": "₹10,000", "severity": "HIGH"},
        {"offence": "Driving Without Insurance", "category": "Documents", "section": "Sec 196 MVA", "first_offence": "₹2,000 or 3 months imprisonment or both", "repeat_offence": "₹4,000 or 3 months imprisonment or both", "severity": "HIGH"},
        {"offence": "Driving Without Registration", "category": "Documents", "section": "Sec 192 MVA", "first_offence": "₹5,000", "repeat_offence": "₹10,000", "severity": "HIGH"},
        {"offence": "Vehicle Overloading (Passengers)", "category": "Overloading", "section": "Sec 194A MVA", "first_offence": "₹1,000 per extra passenger", "repeat_offence": "₹1,000 per extra passenger", "severity": "MEDIUM"},
        {"offence": "Vehicle Overloading (Goods)", "category": "Overloading", "section": "Sec 194 MVA", "first_offence": "₹20,000 + ₹2,000 per extra tonne", "repeat_offence": "₹20,000 + ₹2,000 per extra tonne", "severity": "HIGH"},
        {"offence": "Dangerous / Rash Driving", "category": "Reckless Driving", "section": "Sec 184 MVA", "first_offence": "₹5,000 or 6 months imprisonment or both", "repeat_offence": "₹10,000 or 2 years imprisonment or both", "severity": "HIGH"},
        {"offence": "Jumping Red Light", "category": "Traffic Signal", "section": "Sec 177 MVA", "first_offence": "₹1,000", "repeat_offence": "₹2,000", "severity": "MEDIUM"},
        {"offence": "Wrong Side Driving", "category": "Reckless Driving", "section": "Sec 184 MVA", "first_offence": "₹5,000", "repeat_offence": "₹10,000", "severity": "HIGH"},
        {"offence": "No Pollution Under Control (PUC) Certificate", "category": "Documents", "section": "Sec 190(2) MVA", "first_offence": "₹10,000 or 6 months imprisonment or both", "repeat_offence": "₹10,000 or 6 months imprisonment or both", "severity": "HIGH"},
        {"offence": "Driving Without Valid Fitness Certificate", "category": "Documents", "section": "Sec 192 MVA", "first_offence": "₹5,000", "repeat_offence": "₹10,000", "severity": "HIGH"},
        {"offence": "Obstruction / Illegal Parking", "category": "Parking", "section": "Sec 177 MVA", "first_offence": "₹500", "repeat_offence": "₹1,500", "severity": "LOW"},
        {"offence": "Not Giving Way to Emergency Vehicle", "category": "Emergency", "section": "Sec 194E MVA", "first_offence": "₹10,000 or 6 months imprisonment or both", "repeat_offence": "₹10,000 or 6 months imprisonment or both", "severity": "HIGH"},
        {"offence": "Unauthorised Use of Horn / Air Horn", "category": "Noise", "section": "Sec 190(2) MVA", "first_offence": "₹1,000", "repeat_offence": "₹2,000", "severity": "LOW"},
        {"offence": "Racing / Speeding Contest on Road", "category": "Reckless Driving", "section": "Sec 189 MVA", "first_offence": "₹5,000 or 1 month imprisonment or both", "repeat_offence": "₹10,000 or 1 month imprisonment or both", "severity": "HIGH"},
        {"offence": "Minor Driving Vehicle", "category": "Licence", "section": "Sec 199A MVA", "first_offence": "Guardian/owner fined ₹25,000 + 3 years imprisonment, vehicle registration cancelled", "repeat_offence": "Guardian/owner fined ₹25,000 + 3 years imprisonment", "severity": "HIGH"},
        {"offence": "Not Carrying Driving Licence", "category": "Licence", "section": "Sec 130 MVA", "first_offence": "₹500", "repeat_offence": "₹500", "severity": "LOW"},
        {"offence": "Tinted Glass (Violating VLT norms)", "category": "Vehicle Condition", "section": "Sec 190 MVA", "first_offence": "₹100 per day", "repeat_offence": "₹300 per day", "severity": "LOW"},
    ]

    categories = ["All"] + sorted(list(set(f["category"] for f in FINES_DB)))
    severities = ["All", "HIGH", "MEDIUM", "LOW"]

    # ── Search & Filter ───────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([3, 1.5, 1.5])
    with col1:
        search_query = st.text_input("🔍 Search Offence", placeholder="e.g. helmet, drunk, mobile, insurance...")
    with col2:
        filter_cat = st.selectbox("Category", categories)
    with col3:
        filter_sev = st.selectbox("Severity", severities)

    # Filter logic
    results = FINES_DB
    if search_query:
        results = [f for f in results if search_query.lower() in f["offence"].lower() or search_query.lower() in f["section"].lower()]
    if filter_cat != "All":
        results = [f for f in results if f["category"] == filter_cat]
    if filter_sev != "All":
        results = [f for f in results if f["severity"] == filter_sev]

    st.markdown(f'<div style="color:#5a5040;font-size:0.75rem;margin-bottom:1rem;">{len(results)} offence(s) found</div>', unsafe_allow_html=True)

    # ── Results ───────────────────────────────────────────────────────────────
    if results:
        for fine in results:
            sev = fine["severity"]
            sev_cls = {"HIGH": "risk-high", "MEDIUM": "risk-medium", "LOW": "risk-low"}.get(sev, "")
            sev_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "")

            st.markdown(f"""
<div style="background:#111318;border:1px solid #c9a84c22;border-radius:6px;padding:1.2rem 1.5rem;margin-bottom:0.8rem;">
  <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:0.8rem;">
    <div>
      <span style="color:#c9a84c;font-size:0.95rem;font-weight:600;">{fine['offence']}</span>
      <span style="background:#1a1710;border:1px solid #c9a84c33;color:#c9a84c;padding:2px 8px;border-radius:2px;font-size:0.65rem;margin-left:8px;letter-spacing:1px;">{fine['section']}</span>
    </div>
    <span class="{sev_cls}" style="font-size:0.72rem;">{sev_icon} {sev}</span>
  </div>
  <div style="display:flex;gap:1.5rem;flex-wrap:wrap;">
    <div>
      <div style="color:#5a5040;font-size:0.65rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:3px;">First Offence</div>
      <div style="color:#d4c9b0;font-size:0.85rem;">{fine['first_offence']}</div>
    </div>
    <div style="border-left:1px solid #c9a84c22;padding-left:1.5rem;">
      <div style="color:#5a5040;font-size:0.65rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:3px;">Repeat Offence</div>
      <div style="color:#ff6b6b;font-size:0.85rem;">{fine['repeat_offence']}</div>
    </div>
  </div>
  <div style="margin-top:8px;">
    <span style="background:#111318;border:1px solid #333;color:#6a6050;padding:2px 8px;border-radius:2px;font-size:0.68rem;">{fine['category']}</span>
  </div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="result-card"><div style="color:#5a5040;">No offences found. Try a different search term.</div></div>', unsafe_allow_html=True)

    # ── Summary stats ─────────────────────────────────────────────────────────
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    high = len([f for f in FINES_DB if f["severity"] == "HIGH"])
    med  = len([f for f in FINES_DB if f["severity"] == "MEDIUM"])
    low  = len([f for f in FINES_DB if f["severity"] == "LOW"])
    with c1:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{len(FINES_DB)}</div><div class="metric-label">Total Offences</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-box"><div class="metric-val" style="color:#ff6b6b;">{high}</div><div class="metric-label">High Severity</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-box"><div class="metric-val" style="color:#ffcc55;">{med}</div><div class="metric-label">Medium Severity</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-box"><div class="metric-val" style="color:#66bb88;">{low}</div><div class="metric-label">Low Severity</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="disclaimer">⚠ Fines as per Motor Vehicles (Amendment) Act, 2019. Actual fines may vary by state. Verify with official sources before legal proceedings.</div>', unsafe_allow_html=True)
