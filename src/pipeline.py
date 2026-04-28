"""
pipeline.py — All legal analysis features powered by InferenceEngine
"""
import os, sys, re
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from legal_kb        import VICTIM_PHRASES, FAULT_PHRASES
from inference_engine import get_engine


# ═══════════════════════════════════════════════════════════════════════════════
# 1. FULL CASE ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
def analyze_case(description: str) -> dict:
    engine   = get_engine()
    sections = engine.predict_sections(description)
    fault    = detect_fault(description)
    risk     = assess_risk(sections, fault["status"])
    return {
        "sections_identified": sections,
        "total_sections":      len(sections),
        "model_used":          engine.mode,
        "fault_status":        fault["status"],
        "fault_analysis":      fault["message"],
        "risk_assessment":     risk,
        "recommendations":     build_recommendations(sections, fault["status"], risk),
        "landmark_cases":      get_landmark_cases(sections),
        "your_rights":         get_rights(fault["status"], sections),
        "next_steps":          get_next_steps(fault["status"]),
        "document_checklist":  get_document_checklist_for_sections(sections),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. FAULT DETECTION
# ═══════════════════════════════════════════════════════════════════════════════
def detect_fault(description: str) -> dict:
    text        = description.lower()
    is_victim   = any(p in text for p in VICTIM_PHRASES)
    is_at_fault = any(p in text for p in FAULT_PHRASES)

    if is_at_fault and not is_victim:
        return {"status": "AT_FAULT", "message": (
            "Based on the description, you appear to be the ACCUSED party. "
            "The identified sections may be applicable against you. "
            "Consult a criminal defence lawyer immediately before speaking to police."
        )}
    elif is_victim and not is_at_fault:
        return {"status": "VICTIM", "message": (
            "Based on the description, you appear to be the VICTIM. "
            "You have the right to file an FIR, seek compensation, and pursue legal remedies."
        )}
    elif is_at_fault and is_victim:
        return {"status": "BOTH", "message": (
            "The situation involves mutual fault. Both parties may face legal liability. "
            "Consult an advocate to assess the exact legal position of each party."
        )}
    return {"status": "UNCLEAR", "message": (
        "Fault position could not be automatically determined. "
        "Provide more specific details about the incident, or consult a lawyer."
    )}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. RISK ASSESSMENT
# ═══════════════════════════════════════════════════════════════════════════════
def assess_risk(sections: list, fault_status: str) -> dict:
    non_bailable = [s for s in sections if s.get("bailable") == False]
    cognizable   = [s for s in sections if s.get("cognizable") == True]
    nb_count     = len(non_bailable)

    if nb_count >= 3 or (nb_count >= 1 and fault_status == "AT_FAULT"):
        level = "HIGH"
    elif nb_count >= 1:
        level = "MEDIUM"
    elif sections:
        level = "LOW"
    else:
        level = "UNKNOWN"

    desc_map = {
        "HIGH":    "🔴 Immediate legal intervention required. Arrest is likely.",
        "MEDIUM":  "🟡 Significant legal risk. Professional advice strongly recommended.",
        "LOW":     "🟢 Lower legal risk. Bailable offences — bail can be granted by police.",
        "UNKNOWN": "⚪ Cannot assess risk without more information.",
    }

    return {
        "level":              level,
        "description":        desc_map[level],
        "non_bailable_count": nb_count,
        "cognizable_count":   len(cognizable),
        "bail_type": (
            "Non-Bailable — Only Sessions Court / High Court can grant bail"
            if nb_count > 0 else
            "Bailable — Police may grant bail"
            if sections else "N/A"
        ),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. SMART RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════════════════
def build_recommendations(sections: list, fault_status: str, risk: dict) -> list:
    if not sections:
        return ["No specific sections matched. Please provide more detailed description."]
    recs = []
    if risk["level"] == "HIGH":
        recs.append("🔴 URGENT: Consult a criminal lawyer IMMEDIATELY before any police interaction.")
        recs.append("Do NOT give any statement to police without a lawyer present.")
    if fault_status == "VICTIM":
        recs.append("📋 File an FIR at the nearest police station under Section 154 CrPC.")
        recs.append("📸 Preserve all evidence: screenshots, photos, videos, voice recordings.")
        recs.append("👥 Note names and contact details of all witnesses.")
        recs.append("🏥 Get a medico-legal certificate (MLC) if physically harmed.")
        cats = {s.get("category","") for s in sections}
        if "Cyber Crime" in cats:
            recs.append("💻 Report cybercrime at cybercrime.gov.in or call 1930.")
        if any("Women" in c for c in cats):
            recs.append("📞 Women helpline: 181 | Police Women Cell: 1091")
    if fault_status == "AT_FAULT":
        recs.append("🛡 Apply for Anticipatory Bail under Section 438 CrPC if arrest is apprehended.")
        recs.append("📞 Contact a criminal defence lawyer immediately.")
        recs.append("🤫 Do not discuss the matter except with your lawyer.")
    nb = [s for s in sections if s.get("bailable") == False]
    if nb:
        recs.append(f"⚖ {len(nb)} non-bailable offence(s) found. Bail requires Sessions Court or High Court.")
    recs.append("📁 Gather all relevant documents: FIR copy, medical reports, bank statements as applicable.")
    recs.append("⚠ AI-generated information. Consult a qualified advocate for legal proceedings.")
    return recs


# ═══════════════════════════════════════════════════════════════════════════════
# 5. LANDMARK CASES
# ═══════════════════════════════════════════════════════════════════════════════
LANDMARK_DB = {
    "Cyber Crime": [
        {"case": "Shreya Singhal v. Union of India (2015)", "court": "Supreme Court of India",
         "relevance": "Struck down Section 66A IT Act; landmark ruling on cyber laws and free speech."},
        {"case": "State of Tamil Nadu v. Suhas Katti (2004)", "court": "Chennai City Civil Court",
         "relevance": "First conviction under IT Act Section 67 for obscene online messages."},
    ],
    "Offences Against Women": [
        {"case": "Vishakha v. State of Rajasthan (1997)", "court": "Supreme Court of India",
         "relevance": "Established Vishakha Guidelines — foundation of POSH Act 2013."},
        {"case": "Mukesh v. State (NCT of Delhi) (2017)", "court": "Supreme Court of India",
         "relevance": "Nirbhaya case — upheld death penalty for gang rape and murder."},
    ],
    "Fraud & Cheating": [
        {"case": "R.K. Dalmia v. Delhi Administration (1962)", "court": "Supreme Court of India",
         "relevance": "Defined scope of cheating and dishonest inducement under Section 420 IPC."},
        {"case": "Iridium India Telecom v. Motorola Inc (2011)", "court": "Supreme Court of India",
         "relevance": "Key judgment on corporate fraud and criminal liability of companies."},
    ],
    "Offences Against Body": [
        {"case": "K.M. Nanavati v. State of Maharashtra (1962)", "court": "Supreme Court of India",
         "relevance": "Distinguished murder from culpable homicide; defined grave and sudden provocation."},
        {"case": "Bachan Singh v. State of Punjab (1980)", "court": "Supreme Court of India",
         "relevance": "Established the 'rarest of rare' doctrine for awarding death penalty."},
    ],
    "Property Offences": [
        {"case": "State of Maharashtra v. Vinayak (1981)", "court": "Supreme Court of India",
         "relevance": "Defined elements of theft and possession under Section 378/379 IPC."},
    ],
    "Corruption": [
        {"case": "Vineet Narain v. Union of India (1998)", "court": "Supreme Court of India",
         "relevance": "Established CBI autonomy; landmark in corruption investigation and rule of law."},
    ],
    "Consumer Protection": [
        {"case": "Spring Meadows Hospital v. Harjol Ahluwalia (1998)", "court": "Supreme Court of India",
         "relevance": "Extended consumer protection to medical services."},
    ],
    "Motor Vehicle": [
        {"case": "Sarla Verma v. Delhi Transport Corporation (2009)", "court": "Supreme Court of India",
         "relevance": "Standardized compensation calculation in motor accident claims."},
    ],
    "Kidnapping & Trafficking": [
        {"case": "State of Haryana v. Raja Ram (1973)", "court": "Supreme Court of India",
         "relevance": "Defined elements of kidnapping and the concept of lawful guardianship under IPC."},
    ],
}

def get_landmark_cases(sections: list) -> list:
    cats = list({s.get("category","") for s in sections})
    results = []
    seen = set()
    for cat in cats:
        for case in LANDMARK_DB.get(cat, []):
            if case["case"] not in seen:
                seen.add(case["case"])
                results.append({**case, "category": cat})
    return results or [{"case": "No specific landmark cases found", "court": "", "relevance": "Consult a lawyer for relevant precedents.", "category": ""}]


# ═══════════════════════════════════════════════════════════════════════════════
# 6. YOUR RIGHTS
# ═══════════════════════════════════════════════════════════════════════════════
def get_rights(fault_status: str, sections: list) -> list:
    rights = [
        "Right to remain silent — Not obligated to make self-incriminating statements (Article 20(3)).",
        "Right to legal representation — Right to be represented by a lawyer (Section 303 CrPC).",
        "Right to know grounds of arrest (Section 50 CrPC).",
        "Right to be produced before Magistrate within 24 hours of arrest (Article 22 + Section 57 CrPC).",
        "Right to free legal aid if you cannot afford a lawyer (Article 39A Constitution).",
    ]
    if fault_status == "VICTIM":
        rights += [
            "Right to file FIR — Police cannot refuse to register an FIR (Section 154 CrPC).",
            "Right to approach Magistrate if police refuses FIR (Section 156(3) CrPC).",
            "Right to compensation under Section 357 CrPC.",
            "Right to get FIR copy free of cost.",
        ]
    if fault_status == "AT_FAULT":
        rights += [
            "Right to Anticipatory Bail (Section 438 CrPC) before arrest.",
            "Right to regular bail after arrest (Section 437/439 CrPC).",
            "Right against double jeopardy — Cannot be tried twice for same offence (Article 20(2)).",
        ]
    if any("Women" in s.get("category","") for s in sections):
        rights += [
            "Right to have statement recorded by a female police officer.",
            "FIR for rape can be filed at any police station (Zero FIR).",
        ]
    return rights


# ═══════════════════════════════════════════════════════════════════════════════
# 7. NEXT STEPS
# ═══════════════════════════════════════════════════════════════════════════════
def get_next_steps(fault_status: str) -> list:
    if fault_status == "VICTIM":
        return [
            "Step 1: File FIR at nearest police station (or cybercrime.gov.in for cyber offences).",
            "Step 2: Obtain MLC (Medico-Legal Certificate) if physically harmed.",
            "Step 3: Consult a lawyer to assess strength of case.",
            "Step 4: Preserve and document all evidence meticulously.",
            "Step 5: Follow up on FIR; if inactive, approach Magistrate directly.",
            "Step 6: Consider filing for interim relief / injunction if safety is at risk.",
        ]
    elif fault_status == "AT_FAULT":
        return [
            "Step 1: Contact a criminal defence lawyer immediately.",
            "Step 2: Apply for Anticipatory Bail under Section 438 CrPC if arrest is likely.",
            "Step 3: Do not tamper with evidence or contact the other party.",
            "Step 4: Cooperate with investigation only through your lawyer.",
            "Step 5: If arrested, exercise right to silence and demand legal representation.",
            "Step 6: Explore possibility of settlement where legally permitted.",
        ]
    return [
        "Step 1: Consult a qualified lawyer with all facts.",
        "Step 2: Document everything related to the incident.",
        "Step 3: Identify and secure witnesses.",
        "Step 4: Do not take any action without legal advice.",
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# 8. DOCUMENT CHECKLIST
# ═══════════════════════════════════════════════════════════════════════════════
CHECKLIST_DB = {
    "Cyber Crime": ["Screenshots of all offensive messages/emails/posts", "Bank statements showing unauthorized transactions",
                    "Complaint acknowledgment from cybercrime.gov.in", "Email headers of phishing/fraud emails", "Device details with date/time settings"],
    "Fraud & Cheating": ["All communication records (emails, WhatsApp, letters)", "Payment receipts and bank statements",
                         "Agreement/contract documents", "Cheque copies and bank dishonour memos", "Witness affidavits"],
    "Offences Against Women": ["Medico-Legal Certificate (MLC) from government hospital", "FIR copy",
                                "Medical examination report", "Call records and messages from accused",
                                "Witness statements", "CCTV footage if available", "Photographs of injuries"],
    "Offences Against Body": ["MLC from government hospital", "Photographs of injuries",
                               "Witness names and contact details", "CCTV footage", "Medical bills", "FIR copy"],
    "Property Offences": ["FIR copy", "Proof of ownership", "Purchase receipts/invoices",
                          "Photographs of stolen/damaged items", "Insurance documents if applicable"],
    "Motor Vehicle": ["FIR/accident report (Panchnama)", "Vehicle RC", "Insurance documents",
                      "Driving licence", "Medical bills", "CCTV/dashcam footage", "Post-mortem report if death occurred"],
    "Consumer Protection": ["Original purchase invoice/bill", "Warranty card", "Photographs of defective product",
                             "All communication with seller", "Bank statements showing payment"],
    "Corruption": ["Audio/video recordings of demand (if any)", "Witness statements",
                   "Documentary evidence of bribe given", "Official documents related to the matter"],
}

def get_document_checklist_for_sections(sections: list) -> dict:
    cats = list({s.get("category","") for s in sections})
    docs = []
    for cat in cats:
        for d in CHECKLIST_DB.get(cat, []):
            if d not in docs:
                docs.append(d)
    return {
        "category_specific": docs or ["All relevant documents related to the incident"],
        "always_required": [
            "Valid identity proof (Aadhaar / Passport / Voter ID)",
            "Passport-size photographs",
            "Copy of all FIRs filed (if any)",
            "Any court orders previously obtained",
        ],
    }

def get_document_checklist(category: str) -> dict:
    docs = CHECKLIST_DB.get(category, ["All relevant documents related to the incident."])
    return {
        "category": category,
        "documents": docs,
        "always_required": [
            "Valid identity proof (Aadhaar / Passport / Voter ID)",
            "Passport-size photographs",
            "Copy of all FIRs filed (if any)",
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 9. FIR DRAFTING
# ═══════════════════════════════════════════════════════════════════════════════
def draft_fir(data: dict) -> dict:
    today = datetime.now().strftime("%d %B %Y")
    section_str = ", ".join(data.get("sections", [])) or "[Applicable IPC Sections]"
    fir = f"""
FIRST INFORMATION REPORT
(Under Section 154, Code of Criminal Procedure, 1973)

Date of Report      : {today}
Police Station      : {data.get('police_station', '[Police Station Name]')}
District            : [District Name]
State               : [State Name]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PARTICULARS OF COMPLAINANT

Name                : {data.get('complainant_name','[Complainant Name]')}
Age                 : {data.get('age','[Age]')}
Father's/Husband's  : [Father/Husband Name]
Address             : {data.get('address','[Address]')}
Phone Number        : [Phone Number]
Occupation          : [Occupation]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PARTICULARS OF ACCUSED

Name of Accused     : {data.get('accused_name','Unknown / [Accused Name]')}
Address of Accused  : [Address of Accused if known]
Description         : [Physical description if unknown]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DETAILS OF OFFENCE

Date & Time         : {data.get('incident_date','[Date and Time]')}
Place of Incident   : {data.get('incident_location','[Location]')}
Applicable Sections : {section_str}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FACTS OF THE CASE

{data.get('incident_description','[Detailed description of incident]')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WITNESSES (if any)

{data.get('witnesses','None known at this time')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRAYER

It is prayed that an FIR be registered against the accused under the
above-mentioned sections and appropriate legal action be taken.

I declare that the information given above is true and correct.

Date : {today}

Signature : _______________________
Name      : {data.get('complainant_name','[Name]')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FOR OFFICE USE ONLY

FIR No.             : ___________
Date of Registration: ___________
Officer In Charge   : ___________
""".strip()
    return {"fir_draft": fir, "generated_on": today,
            "note": "AI-generated draft. Review with a qualified advocate before submission."}


# ═══════════════════════════════════════════════════════════════════════════════
# 10. LEGAL NOTICE
# ═══════════════════════════════════════════════════════════════════════════════
def draft_legal_notice(data: dict) -> dict:
    today = datetime.now().strftime("%d %B %Y")
    section_str = ", ".join(data.get("sections", [])) or "relevant provisions of law"
    notice = f"""
LEGAL NOTICE
(WITHOUT PREJUDICE)

Date: {today}

To,
{data.get('receiver_name','[Receiver Name]')}
{data.get('receiver_address','[Receiver Address]')}

Subject: Legal Notice — {data.get('subject','[Subject]')}

Dear Sir/Madam,

Under instructions from my client, {data.get('sender_name','[Sender Name]')}, residing at
{data.get('sender_address','[Sender Address]')}, I hereby serve this Legal Notice:

1. FACTS:
{data.get('facts','[State the facts]')}

2. LEGAL BASIS:
Your acts/omissions are in violation of {section_str}, entitling my client
to seek appropriate legal remedies against you.

3. DEMAND:
{data.get('demand','[State specific demand]')}

4. CONSEQUENCE OF NON-COMPLIANCE:
Failure to comply within {data.get('deadline_days','15')} days of receipt of this notice
shall constrain my client to initiate civil and/or criminal proceedings at your cost.

This notice is issued without prejudice to all other rights and remedies available.

Yours faithfully,

_______________________
Advocate for {data.get('sender_name','[Client Name]')}
Bar Council No.: [Number]
Date: {today}
""".strip()
    return {"notice_draft": notice, "generated_on": today,
            "note": "AI-generated draft. Review and sign through a qualified advocate before dispatch."}


# ═══════════════════════════════════════════════════════════════════════════════
# 11. BAIL APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════
def draft_bail_application(data: dict) -> dict:
    today = datetime.now().strftime("%d %B %Y")
    section_str = ", ".join(data.get("sections", [])) or "[Applicable Sections]"
    bail = f"""
IN THE COURT OF THE SESSIONS JUDGE / CHIEF JUDICIAL MAGISTRATE
[District], [State]

BAIL APPLICATION
Under Section 437 / 438 / 439 Cr.P.C.

IN THE MATTER OF:
{data.get('accused_name','[Accused Name]')}, Age: {data.get('age','[Age]')}
{data.get('address','[Address]')}
                                                    ...APPLICANT/ACCUSED
VERSUS
STATE OF [STATE]                                    ...RESPONDENT

FIR No.         : {data.get('fir_number','[FIR No.]')}
Police Station  : {data.get('police_station','[Police Station]')}
Offence Under   : {section_str}

GROUNDS FOR BAIL:

1. {data.get('grounds', 'The accused has no prior criminal record and will cooperate with investigation.')}
2. The applicant is a permanent resident and is not likely to abscond.
3. The applicant undertakes to appear before the Investigating Officer / Court as required.
4. The applicant has no history of tampering with evidence.
5. Continued detention would cause irreparable harm to applicant and their family.

PRAYER:
It is prayed that this Hon'ble Court may be pleased to:
(a) Release the applicant on bail pending investigation / trial;
(b) Impose conditions as deemed fit and proper;
(c) Pass any other order as deemed just.

Date: {today}

Through Advocate:
_______________________
[Advocate Name], Bar Council No.: [Number]

Applicant's Signature: _______________________
""".strip()
    return {"bail_application_draft": bail, "generated_on": today,
            "note": "AI-generated draft. Must be reviewed and filed by a qualified advocate."}
