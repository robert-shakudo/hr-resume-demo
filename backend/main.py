import time
import asyncio
import copy
import re
import random
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from mock_data import APPLICANTS, JOB_POSTING, score_applicant

app = FastAPI(title="HR Resume Processing Demo")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_applicant_store: dict = {a["id"]: dict(a) for a in APPLICANTS}
_scores_cache: dict = {}

DEFAULT_SETTINGS = {
    "scoring": {
        "auto_promote_threshold": 75,
        "strong_hire_threshold": 75,
        "consider_threshold": 55,
    },
    "email": {
        "mode": "mock",
        "mock_email": "test@yourdomain.com",
        "real_email": "",
        "subject": "Interview Invitation — Ski Lift Operator at Vail Mountain",
        "template": "Hi {{first_name}},\n\nWe reviewed your application and were impressed by your background{{ski_experience_note}}.\n\nWe'd love to invite you for a 30-minute interview for the Ski Lift Operator position at Vail Mountain.\n\n{{interview_details}}\n\nTo help us prepare, here are a few questions we'd love for you to reflect on:\n\n{{interview_questions}}\n\nPlease reply to confirm your availability.\n\nBest regards,\nMountain Operations HR Team",
        "interview_details": "We have availability this week — Tuesday through Thursday, 8am–4pm.",
    },
    "questions": [
        "Can you describe your experience operating ski lifts or similar equipment?",
        "Are you available to work weekends, holidays, and early morning shifts starting at 6am?",
        "Do you hold any safety certifications (OSHA, First Aid, CPR)?",
        "How do you handle a situation where a guest refuses to follow safety instructions?",
        "What's your experience working in cold outdoor conditions for extended periods?",
        "How would you respond if the lift stopped unexpectedly with guests on board?",
    ],
}

_settings = copy.deepcopy(DEFAULT_SETTINGS)

MOCK_RESPONSES_HIGH = [
    "Hi, thank you so much for the invitation! I'm really excited about this opportunity. I can confirm I'm available on March 5th. I have {ski_years} years of lift experience and hold my OSHA certification — safety is always my top priority. I'm available weekends, holidays, and early morning shifts. Looking forward to meeting the team!",
    "Thank you for reaching out! I'd love to come in for an interview. I've been working ski resort operations for {ski_years} seasons and I'm passionate about guest safety. I can confirm availability on March 5th. All my certifications are current. See you then!",
]
MOCK_RESPONSES_MED = [
    "Hi, thanks for the email. I can make the interview on March 5th. I'm available weekends and I'm eager to learn the lift operation procedures. I don't have direct lift experience but I'm physically fit and a quick learner.",
    "Hello, thank you for the invitation. I'm interested in the position and available for the interview. I have some outdoor experience and can work mornings and weekends. Happy to discuss further.",
]
MOCK_RESPONSES_LOW = [
    "Thanks. I can come in. I live a bit far but I can arrange transport. Let me know the exact time.",
    "Hi, got your email. I'm available. I haven't worked at a ski resort before but I'm willing to try. When should I come?",
]


def _pick_questions_for_candidate(applicant: dict) -> list[str]:
    questions = _settings["questions"]
    ski_jobs = [e for e in applicant["resume"]["experience"] if e.get("ski_related")]
    certs = applicant["resume"].get("certifications", [])
    avail = applicant["resume"].get("availability", {})

    picked = []
    if ski_jobs:
        for q in questions:
            if "lift" in q.lower() or "equipment" in q.lower():
                picked.append(q)
                break
    if not avail.get("weekends") or not avail.get("early_am"):
        for q in questions:
            if "available" in q.lower() or "shift" in q.lower():
                picked.append(q)
                break
    if not certs:
        for q in questions:
            if "certif" in q.lower() or "osha" in q.lower():
                picked.append(q)
                break
    for q in questions:
        if "safety" in q.lower() and q not in picked:
            picked.append(q)
            break
    if len(picked) < 2 and questions:
        for q in questions:
            if q not in picked:
                picked.append(q)
            if len(picked) >= 3:
                break
    return picked[:3]


def _render_email(template: str, applicant: dict, score_data) -> str:
    ski_years = sum(e.get("years", 0) for e in applicant["resume"]["experience"] if e.get("ski_related"))
    certs = applicant["resume"].get("certifications", [])
    cert_str = ", ".join(certs[:2]) if certs else ""

    ski_note = ""
    if ski_years > 0:
        ski_note = f" — particularly your {ski_years} year{'s' if ski_years > 1 else ''} of ski resort experience"
    elif cert_str:
        ski_note = f" — especially your {cert_str} certifications"

    questions = _pick_questions_for_candidate(applicant)
    questions_block = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))

    out = template
    out = out.replace("{{first_name}}", applicant["first_name"])
    out = out.replace("{{last_name}}", applicant["last_name"])
    out = out.replace("{{ski_experience_note}}", ski_note)
    out = out.replace("{{interview_details}}", _settings["email"]["interview_details"])
    out = out.replace("{{interview_questions}}", questions_block)
    out = out.replace("{{location}}", applicant.get("location", ""))
    if score_data:
        out = out.replace("{{score}}", str(score_data.get("score", "")))
    return out


def _score_response(text: str, applicant: dict) -> dict:
    text_lower = text.lower()
    score = 0
    breakdown = {}
    reasons = []

    enth_words = ["excited", "love", "passion", "great", "perfect", "excellent", "happy", "thrilled", "looking forward", "eager", "enthusiastic"]
    enth_pts = min(15, sum(1 for w in enth_words if w in text_lower) * 5)
    score += enth_pts
    breakdown["Enthusiasm"] = {"points": enth_pts, "max": 15}
    if enth_pts >= 10:
        reasons.append("✅ Strong enthusiasm and positive tone")
    elif enth_pts >= 5:
        reasons.append("⚠️ Moderate enthusiasm")
    else:
        reasons.append("❌ Low enthusiasm in response")

    skill_words = ["osha", "lift", "safety", "certified", "cert", "experience", "season", "resort", "mountain", "operator"]
    skill_pts = min(15, sum(1 for w in skill_words if w in text_lower) * 3)
    score += skill_pts
    breakdown["Relevant Content"] = {"points": skill_pts, "max": 15}
    if skill_pts >= 9:
        reasons.append("✅ Mentions relevant skills and experience")
    elif skill_pts > 0:
        reasons.append("⚠️ Some relevant content")
    else:
        reasons.append("❌ No relevant skills mentioned")

    avail_words = ["available", "confirm", "works for me", "can make it", "yes", "weekend", "morning", "holiday"]
    avail_pts = min(10, sum(1 for w in avail_words if w in text_lower) * 4)
    score += avail_pts
    breakdown["Availability Confirmation"] = {"points": avail_pts, "max": 10}
    if avail_pts >= 8:
        reasons.append("✅ Confirmed availability clearly")
    elif avail_pts > 0:
        reasons.append("⚠️ Partial availability confirmation")
    else:
        reasons.append("❌ Availability not confirmed")

    word_count = len(text.split())
    detail_pts = min(10, word_count // 5)
    score += detail_pts
    breakdown["Response Detail"] = {"points": detail_pts, "max": 10}
    if detail_pts >= 8:
        reasons.append("✅ Detailed, well-written response")
    elif detail_pts >= 4:
        reasons.append("⚠️ Brief response")
    else:
        reasons.append("❌ Very brief response")

    total = min(50, score)
    rec = "Strong" if total >= 35 else "Adequate" if total >= 20 else "Weak"
    return {"score": total, "max_score": 50, "recommendation": rec, "breakdown": breakdown, "reasons": reasons}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/job")
def get_job():
    return JOB_POSTING


@app.get("/api/applicants")
def get_applicants():
    result = []
    for a in _applicant_store.values():
        entry = dict(a)
        if a["id"] in _scores_cache:
            entry["score_data"] = _scores_cache[a["id"]]
        result.append(entry)
    result.sort(key=lambda x: x.get("score_data", {}).get("score", -1), reverse=True)
    return result


@app.get("/api/applicants/{applicant_id}")
def get_applicant(applicant_id: str):
    if applicant_id not in _applicant_store:
        raise HTTPException(404, "Applicant not found")
    a = dict(_applicant_store[applicant_id])
    if applicant_id in _scores_cache:
        a["score_data"] = _scores_cache[applicant_id]
    return a


@app.post("/api/score/all")
async def score_all():
    threshold = _settings["scoring"]["auto_promote_threshold"]
    scored = []
    auto_promoted = 0
    for applicant_id, applicant in _applicant_store.items():
        await asyncio.sleep(0.05)
        result = score_applicant(applicant)
        _scores_cache[applicant_id] = result
        if result["score"] >= threshold and _applicant_store[applicant_id]["status"] == "new":
            _applicant_store[applicant_id]["status"] = "reviewing"
            auto_promoted += 1
        scored.append({"id": applicant_id, **result})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"scored": len(scored), "auto_promoted": auto_promoted, "threshold": threshold, "results": scored}


@app.post("/api/score/{applicant_id}")
def score_one(applicant_id: str):
    if applicant_id not in _applicant_store:
        raise HTTPException(404, "Applicant not found")
    result = score_applicant(_applicant_store[applicant_id])
    _scores_cache[applicant_id] = result
    return result


class StatusUpdate(BaseModel):
    status: str


@app.patch("/api/applicants/{applicant_id}/status")
def update_status(applicant_id: str, body: StatusUpdate):
    if applicant_id not in _applicant_store:
        raise HTTPException(404, "Applicant not found")
    valid = {"new", "reviewing", "shortlisted", "awaiting_reply", "booked", "rejected", "hired"}
    if body.status not in valid:
        raise HTTPException(400, f"Status must be one of: {valid}")
    _applicant_store[applicant_id]["status"] = body.status
    return {"id": applicant_id, "status": body.status}


class PreviewRequest(BaseModel):
    applicant_ids: list[str]


@app.post("/api/email/preview")
def preview_emails(body: PreviewRequest):
    template = _settings["email"]["template"]
    subject = _settings["email"]["subject"]
    mode = _settings["email"]["mode"]
    previews = []
    for aid in body.applicant_ids:
        if aid not in _applicant_store:
            continue
        applicant = _applicant_store[aid]
        sd = _scores_cache.get(aid)
        questions = _pick_questions_for_candidate(applicant)
        previews.append({
            "id": aid,
            "name": f"{applicant['first_name']} {applicant['last_name']}",
            "email": applicant["email"] if mode == "real" else _settings["email"].get("mock_email", "test@demo.com"),
            "actual_email": applicant["email"],
            "subject": subject,
            "body": _render_email(template, applicant, sd),
            "questions": questions,
            "mode": mode,
        })
    return {"previews": previews, "mode": mode}


class BulkAction(BaseModel):
    applicant_ids: list[str]
    action: str


@app.post("/api/bulk")
def bulk_action(body: BulkAction):
    results = []
    for aid in body.applicant_ids:
        if aid not in _applicant_store:
            continue
        applicant = _applicant_store[aid]
        name = f"{applicant['first_name']} {applicant['last_name']}"
        sd = _scores_cache.get(aid)

        if body.action == "send_invite":
            email_body = _render_email(_settings["email"]["template"], applicant, sd)
            mode = _settings["email"]["mode"]
            to_email = applicant["email"] if mode == "real" else _settings["email"].get("mock_email", "test@demo.com")
            results.append({
                "id": aid, "name": name, "email": to_email, "actual_email": applicant["email"],
                "action": "invite_sent", "mode": mode,
                "subject": _settings["email"]["subject"], "body": email_body,
            })
            _applicant_store[aid]["status"] = "awaiting_reply"
            _applicant_store[aid]["email_sent_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")

        elif body.action == "reject":
            results.append({"id": aid, "name": name, "action": "rejected"})
            _applicant_store[aid]["status"] = "rejected"

        elif body.action == "book_interview":
            slot_hour = 8 + (len(results) % 8)
            calendar_event = {
                "title": f"Ski Lift Operator Interview — {name}",
                "date": "2026-03-05",
                "time": f"{slot_hour:02d}:00",
                "location": "Vail Mountain Operations HQ, Room A2",
                "duration": "30 min",
            }
            results.append({"id": aid, "name": name, "action": "interview_booked", "calendar_event": calendar_event})
            _applicant_store[aid]["status"] = "booked"
            _applicant_store[aid]["calendar_event"] = calendar_event

    return {"action": body.action, "processed": len(results), "results": results}


@app.post("/api/simulate-response/{applicant_id}")
def simulate_response(applicant_id: str):
    if applicant_id not in _applicant_store:
        raise HTTPException(404, "Applicant not found")
    applicant = _applicant_store[applicant_id]
    sd = _scores_cache.get(applicant_id)
    resume_score = sd["score"] if sd else 50

    ski_years = sum(e.get("years", 0) for e in applicant["resume"]["experience"] if e.get("ski_related"))
    first = applicant["first_name"]

    if resume_score >= 75:
        template = random.choice(MOCK_RESPONSES_HIGH)
    elif resume_score >= 50:
        template = random.choice(MOCK_RESPONSES_MED)
    else:
        template = random.choice(MOCK_RESPONSES_LOW)

    response_text = template.format(
        first_name=first,
        ski_years=ski_years if ski_years > 0 else "a few",
        company=applicant["resume"]["experience"][0]["company"] if applicant["resume"]["experience"] else "my previous resort",
    )
    response_score = _score_response(response_text, applicant)
    response_data = {
        "text": response_text,
        "received_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        **response_score,
    }
    _applicant_store[applicant_id]["response_data"] = response_data
    return {"id": applicant_id, "response_data": response_data}


class ScoreResponseRequest(BaseModel):
    applicant_id: str
    text: str


@app.post("/api/score-response")
def score_response_endpoint(body: ScoreResponseRequest):
    if body.applicant_id not in _applicant_store:
        raise HTTPException(404, "Applicant not found")
    applicant = _applicant_store[body.applicant_id]
    result = _score_response(body.text, applicant)
    _applicant_store[body.applicant_id]["response_data"] = {
        "text": body.text,
        "received_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        **result,
    }
    return result


class CandidateReply(BaseModel):
    applicant_id: str
    message: str


@app.post("/api/simulate-reply")
def simulate_candidate_reply(body: CandidateReply):
    if body.applicant_id not in _applicant_store:
        raise HTTPException(404, "Applicant not found")
    applicant = _applicant_store[body.applicant_id]
    msg_lower = body.message.lower()
    if any(w in msg_lower for w in ["confirm", "yes", "available", "accept"]):
        reply = f"Hi {applicant['first_name']},\n\nThank you for confirming! Your interview is on March 5th at Vail Mountain Operations HQ. Bring a valid ID and any certification documents.\n\nSee you then!\n\nMountain Ops HR"
    elif any(w in msg_lower for w in ["reschedule", "different", "change"]):
        reply = f"Hi {applicant['first_name']},\n\nAbsolutely! We have openings March 6th (9am–3pm) or March 7th (8am–2pm).\n\nMountain Ops HR"
    elif any(w in msg_lower for w in ["salary", "pay", "wage"]):
        reply = f"Hi {applicant['first_name']},\n\nThe position pays $22–26/hour plus a full ski pass. Full details at interview.\n\nMountain Ops HR"
    else:
        reply = f"Hi {applicant['first_name']},\n\nThank you for reaching out! Our team will follow up within 24 hours.\n\nMountain Ops HR"
    return {"applicant": f"{applicant['first_name']} {applicant['last_name']}", "ai_drafted_reply": reply}


@app.get("/api/settings")
def get_settings():
    return _settings


@app.put("/api/settings")
def update_settings(new_settings: dict):
    global _settings
    _settings = new_settings
    return _settings


@app.post("/api/paycom/refresh")
def paycom_refresh():
    global _applicant_store, _scores_cache
    _applicant_store = {a["id"]: dict(a) for a in APPLICANTS}
    _scores_cache = {}
    return {"refreshed": True, "applicant_count": len(_applicant_store)}


class UploadedResume(BaseModel):
    first_name: str
    last_name: str
    email: str
    location: str
    distance_miles: float
    resume_text: str


@app.post("/api/upload-resume")
def upload_resume(body: UploadedResume):
    parsed = _parse_freeform_resume(body.resume_text)
    new_id = f"PAY-UPL-{len(_applicant_store) + 1:04d}"
    applicant = {
        "id": new_id, "first_name": body.first_name, "last_name": body.last_name,
        "email": body.email, "phone": "N/A", "location": body.location,
        "distance_miles": body.distance_miles, "applied_date": time.strftime("%Y-%m-%d"),
        "status": "new", "resume": parsed,
    }
    _applicant_store[new_id] = applicant
    score_result = score_applicant(applicant)
    _scores_cache[new_id] = score_result
    return {"id": new_id, "applicant": applicant, "score_data": score_result}


def _parse_freeform_resume(text: str) -> dict:
    text_lower = text.lower()
    ski_kws = ["ski", "lift", "resort", "snowboard", "mountain"]
    physical_kws = ["outdoor", "construction", "labor", "guide", "patrol", "crew", "ranger"]
    cert_map = {
        "osha 30": "OSHA 30", "osha 10": "OSHA 10", "osha": "OSHA 10",
        "first aid": "First Aid", "cpr": "CPR/AED", "emt": "EMT-B",
        "wfr": "WFR", "ansi": "ANSI/ASME B77.1", "avalanche": "Avalanche Level 1",
        "first responder": "First Responder",
    }
    detected_certs = []
    for kw, label in cert_map.items():
        if kw in text_lower and label not in detected_certs:
            detected_certs.append(label)
    ski_years = 0
    matches = re.findall(r'(\d+)\s*(?:year|season|yr)', text_lower)
    if matches and any(kw in text_lower for kw in ski_kws):
        ski_years = int(matches[0])
    has_ski = any(kw in text_lower for kw in ski_kws)
    experience = []
    if has_ski:
        experience.append({"title": "Ski Resort Worker", "company": "Resort", "years": ski_years or 1, "ski_related": True})
    elif any(kw in text_lower for kw in physical_kws):
        experience.append({"title": "Outdoor/Physical Labor", "company": "Various", "years": 2, "ski_related": False})
    return {
        "summary": text[:300] + ("..." if len(text) > 300 else ""),
        "experience": experience, "certifications": detected_certs,
        "availability": {
            "weekends": any(w in text_lower for w in ["weekend", "saturday", "sunday"]),
            "holidays": "holiday" in text_lower,
            "early_am": any(w in text_lower for w in ["6am", "early morning", "early am", "5am"]),
        },
        "skills": [kw for kw in ski_kws + physical_kws if kw in text_lower][:8],
    }


static_dir = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
