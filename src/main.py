"""
main.py — LexAI v4 FastAPI Application
Run: uvicorn main:app --reload --app-dir src
"""

import os, sys, json, logging

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, _ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("lexai")

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List

from config   import APP_TITLE, APP_VERSION, EVAL_RESULTS_PATH, DATA_DIR
from pipeline import (
    analyze_case, detect_fault, assess_risk,
    build_recommendations, get_landmark_cases, get_rights,
    get_next_steps, get_document_checklist,
    draft_fir, draft_legal_notice, draft_bail_application,
)
from inference_engine import get_engine

# ── Boot ──────────────────────────────────────────────────────────────────────
logger.info("Booting LexAI v4...")
_engine = get_engine()
logger.info(f"Inference engine ready: {_engine.mode}")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="⚖ LexAI — AI Legal Statute Identification System",
    description="""
## LexAI v4 — Real-World AI Legal Assistant for Indian Law

**Dataset**: LeSICiN (IIT Kharagpur / AAAI-22) — Zenodo 6053791  
**ML Model**: InLegalBERT (fine-tuned) + TF-IDF + LinearSVC (baseline)

### Endpoints:
| Endpoint | Feature |
|---|---|
| `POST /analyze` | Full case analysis — sections, fault, risk, rights |
| `POST /draft/fir` | Draft First Information Report |
| `POST /draft/legal-notice` | Draft Legal Notice |
| `POST /draft/bail-application` | Draft Bail Application |
| `POST /checklist` | Document checklist |
| `GET /evaluation` | Model evaluation metrics |
| `GET /model/info` | Active model information |
| `POST /admin/train` | Train / retrain ML models |

> ⚠ AI-generated legal information only. Not a substitute for qualified legal advice.
    """,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── Pydantic schemas ──────────────────────────────────────────────────────────
class CaseInput(BaseModel):
    description: str = Field(..., min_length=15, example="Someone hacked my bank account and transferred Rs 50000 without my knowledge. They also sent me threatening messages on WhatsApp.")

class FIRInput(BaseModel):
    complainant_name:     str
    age:                  str
    address:              str
    incident_description: str
    incident_date:        str
    incident_location:    str
    accused_name:         Optional[str] = "Unknown"
    witnesses:            Optional[str] = "None"
    police_station:       str
    sections:             Optional[List[str]] = []

class LegalNoticeInput(BaseModel):
    sender_name:      str
    sender_address:   str
    receiver_name:    str
    receiver_address: str
    subject:          str
    facts:            str
    demand:           str
    deadline_days:    Optional[str] = "15"
    sections:         Optional[List[str]] = []

class BailInput(BaseModel):
    accused_name:   str
    age:            str
    address:        str
    fir_number:     str
    police_station: str
    sections:       Optional[List[str]] = []
    grounds:        Optional[str] = "The accused has no prior criminal record and undertakes to cooperate fully with the investigation."

class ChecklistInput(BaseModel):
    category: str = Field(..., example="Cyber Crime")

class TrainInput(BaseModel):
    model:     str = Field(default="tfidf", description="tfidf | bert | both")
    max_train: Optional[int] = Field(default=None, description="Limit training samples for quick runs")
    confirm:   bool = Field(default=False)


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    engine = get_engine()
    return f"""<!DOCTYPE html>
<html><head><title>LexAI v4</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Georgia,serif;background:#0a0c0f;color:#d4c9b0;
     display:flex;flex-direction:column;align-items:center;
     justify-content:center;min-height:100vh;padding:2rem;text-align:center}}
h1{{color:#c9a84c;font-size:2.5rem;letter-spacing:6px;margin-bottom:.3rem}}
.v{{color:#5a5040;font-size:.75rem;letter-spacing:3px;margin-bottom:.5rem}}
.sub{{color:#7a7060;letter-spacing:2px;margin-bottom:.5rem;font-size:.85rem}}
.badge{{display:inline-block;background:#1a1710;border:1px solid #c9a84c44;
        color:#c9a84c;font-size:.65rem;letter-spacing:2px;
        padding:4px 12px;border-radius:2px;margin-bottom:2.5rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
       gap:.8rem;max-width:900px;width:100%;margin-bottom:2rem}}
.card{{background:#111318;border:1px solid #c9a84c22;border-radius:4px;
       padding:1rem;transition:border-color .2s;text-align:left}}
.card:hover{{border-color:#c9a84c66}}
.card h3{{color:#c9a84c;font-size:.75rem;letter-spacing:2px;margin-bottom:.4rem;text-transform:uppercase}}
.card p{{color:#6a6050;font-size:.72rem;line-height:1.5}}
.links{{display:flex;gap:.8rem;flex-wrap:wrap;justify-content:center}}
a{{background:#1a1710;border:1px solid #c9a84c44;color:#c9a84c;
   padding:8px 20px;text-decoration:none;border-radius:3px;
   font-size:.8rem;letter-spacing:1px;transition:background .2s}}
a:hover{{background:#221e12}}
.model-badge{{background:#0f1a10;border:1px solid #4a8050;color:#6ab070;
              font-size:.65rem;letter-spacing:1px;padding:3px 10px;
              border-radius:2px;margin-bottom:1.5rem;display:inline-block}}
</style></head><body>
<h1>⚖ LEXAI</h1>
<div class="v">VERSION {APP_VERSION}</div>
<p class="sub">AI Legal Statute Identification System · Indian Law</p>
<div class="badge">LeSICiN Dataset · IIT Kharagpur · AAAI-22 · Zenodo 6053791</div>
<div class="model-badge">Active Model: {engine.mode}</div>
<div class="grid">
  <div class="card"><h3>Case Analysis</h3><p>Identify IPC/IT Act sections. ML-powered with InLegalBERT</p></div>
  <div class="card"><h3>Fault Detection</h3><p>Determine if you are victim or accused</p></div>
  <div class="card"><h3>Risk Assessment</h3><p>HIGH/MEDIUM/LOW with bail type analysis</p></div>
  <div class="card"><h3>FIR Drafting</h3><p>Generate formal First Information Report</p></div>
  <div class="card"><h3>Legal Notice</h3><p>Draft professional legal notices</p></div>
  <div class="card"><h3>Bail Application</h3><p>Draft bail application under CrPC</p></div>
  <div class="card"><h3>Landmark Cases</h3><p>Relevant Supreme Court judgments</p></div>
  <div class="card"><h3>Know Your Rights</h3><p>Constitutional and statutory rights</p></div>
</div>
<div class="links">
  <a href="/docs">📘 Swagger UI</a>
  <a href="/redoc">📗 ReDoc</a>
  <a href="/evaluation">📊 Evaluation</a>
  <a href="/model/info">🤖 Model Info</a>
</div>
</body></html>"""


@app.get("/health")
def health():
    return {"status": "ok", "system": "LexAI", "version": APP_VERSION, "model": get_engine().mode}


@app.get("/model/info", summary="Active Model Information")
def model_info():
    return get_engine().get_model_info()


@app.get("/sections", summary="All IPC Sections in Knowledge Base")
def all_sections():
    from legal_kb import IPC_SECTIONS
    return {
        "sections": [{k:v for k,v in s.items() if k!="keywords"} for s in IPC_SECTIONS],
        "total": len(IPC_SECTIONS),
    }


@app.get("/categories", summary="All Legal Categories")
def categories():
    from legal_kb import IPC_SECTIONS
    cats = sorted({s["category"] for s in IPC_SECTIONS})
    return {"categories": cats, "total": len(cats)}


@app.get("/evaluation", summary="Model Evaluation Results")
def evaluation():
    if not os.path.exists(EVAL_RESULTS_PATH):
        return JSONResponse(
            status_code=200,
            content={"message": "No evaluation results yet. Train the model first via POST /admin/train",
                     "instructions": "Download dataset from https://zenodo.org/records/6053791, place files in datasets/ folder, then POST /admin/train"}
        )
    with open(EVAL_RESULTS_PATH) as f:
        return json.load(f)


# ── 1. Case Analysis ──────────────────────────────────────────────────────────
@app.post("/analyze", summary="Full Case Analysis",
          description="Submit case description → sections, fault, risk, rights, recommendations, landmark cases, document checklist.")
def analyze(payload: CaseInput):
    try:
        result = analyze_case(payload.description.strip())
        result["disclaimer"] = "AI-generated legal information only. Not a substitute for professional legal advice."
        return result
    except Exception as e:
        raise HTTPException(500, f"Analysis error: {e}")


# ── 2. FIR ────────────────────────────────────────────────────────────────────
@app.post("/draft/fir", summary="Draft First Information Report")
def create_fir(payload: FIRInput):
    try:
        return draft_fir(payload.model_dump())
    except Exception as e:
        raise HTTPException(500, f"FIR error: {e}")


# ── 3. Legal Notice ───────────────────────────────────────────────────────────
@app.post("/draft/legal-notice", summary="Draft Legal Notice")
def create_notice(payload: LegalNoticeInput):
    try:
        return draft_legal_notice(payload.model_dump())
    except Exception as e:
        raise HTTPException(500, f"Notice error: {e}")


# ── 4. Bail Application ───────────────────────────────────────────────────────
@app.post("/draft/bail-application", summary="Draft Bail Application")
def create_bail(payload: BailInput):
    try:
        return draft_bail_application(payload.model_dump())
    except Exception as e:
        raise HTTPException(500, f"Bail error: {e}")


# ── 5. Document Checklist ─────────────────────────────────────────────────────
@app.post("/checklist", summary="Document Checklist by Category")
def checklist(payload: ChecklistInput):
    try:
        return get_document_checklist(payload.category)
    except Exception as e:
        raise HTTPException(500, f"Checklist error: {e}")


# ── 6. Train / Retrain ────────────────────────────────────────────────────────
@app.post("/admin/train", summary="Train / Retrain ML Models",
          description="Trains TF-IDF and/or BERT model on LeSICiN dataset. Requires dataset files in datasets/ folder.")
def train_models(payload: TrainInput):
    if not payload.confirm:
        raise HTTPException(400, "Set confirm=true to start training.")

    train_file = os.path.join(DATA_DIR, "train.jsonl")
    if not os.path.exists(train_file):
        raise HTTPException(400, (
            "Dataset not found. Download from https://zenodo.org/records/6053791 "
            "and place train.jsonl, dev.jsonl, test.jsonl, label_vocab.json, secs.jsonl "
            f"in the '{DATA_DIR}' folder."
        ))

    try:
        from trainer import train_tfidf, train_bert, save_evaluation_report
        from data_loader import load_all_splits
        data    = load_all_splits(payload.max_train)
        results = {}

        if payload.model in ("tfidf", "both"):
            results["tfidf"] = train_tfidf(data)
        if payload.model in ("bert", "both"):
            results["bert"]  = train_bert(data, payload.max_train)

        report = save_evaluation_report(results, data["train_stats"])

        # Reload engine with new models
        from inference_engine import get_engine
        import inference_engine
        inference_engine._engine = None
        new_engine = get_engine()

        return {"status": "success", "model": new_engine.mode, "results": results}
    except Exception as e:
        raise HTTPException(500, f"Training error: {e}")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, app_dir=_HERE)
