import time
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

from mock_data import APPLICANTS, JOB_POSTING, score_applicant

app = FastAPI(title="HR Resume Processing Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_applicant_store = {a["id"]: dict(a) for a in APPLICANTS}
_scores_cache: dict = {}


@app.get("/api/health")
def health():
    return {"status": "ok", "demo": "HR Resume Processing — Ski Lift Operator"}


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
    scored = []
    for applicant_id, applicant in _applicant_store.items():
        await asyncio.sleep(0.05)
        result = score_applicant(applicant)
        _scores_cache[applicant_id] = result
        scored.append({"id": applicant_id, **result})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"scored": len(scored), "results": scored}


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
    valid = {"new", "reviewing", "shortlisted", "rejected", "hired"}
    if body.status not in valid:
        raise HTTPException(400, f"Status must be one of: {valid}")
    _applicant_store[applicant_id]["status"] = body.status
    return {"id": applicant_id, "status": body.status}


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

        if body.action == "send_invite":
            results.append({
                "id": aid,
                "name": name,
                "email": applicant["email"],
                "action": "invite_sent",
                "message": f"Interview invite sent to {applicant['email']}",
                "subject": "Interview Invitation — Ski Lift Operator at Vail Mountain",
                "body": f"Hi {applicant['first_name']},\n\nWe reviewed your application and are impressed with your background. We'd love to schedule a 30-minute interview for the Ski Lift Operator position.\n\nPlease reply to confirm your availability this week.\n\nBest,\nMountain Ops HR Team",
            })
            _applicant_store[aid]["status"] = "shortlisted"

        elif body.action == "reject":
            results.append({
                "id": aid,
                "name": name,
                "action": "rejected",
                "message": f"Rejection email sent to {applicant['email']}",
            })
            _applicant_store[aid]["status"] = "rejected"

        elif body.action == "book_interview":
            slot_hour = 8 + (len(results) % 8)
            results.append({
                "id": aid,
                "name": name,
                "action": "interview_booked",
                "message": f"Google Calendar invite created for {name}",
                "calendar_event": {
                    "title": f"Ski Lift Operator Interview — {name}",
                    "date": "2026-03-05",
                    "time": f"{slot_hour:02d}:00 AM",
                    "location": "Vail Mountain Operations HQ",
                    "duration": "30 min",
                },
            })

    return {"action": body.action, "processed": len(results), "results": results}


class CandidateReply(BaseModel):
    applicant_id: str
    message: str


@app.post("/api/simulate-reply")
def simulate_candidate_reply(body: CandidateReply):
    if body.applicant_id not in _applicant_store:
        raise HTTPException(404, "Applicant not found")
    applicant = _applicant_store[body.applicant_id]
    name = f"{applicant['first_name']} {applicant['last_name']}"

    msg_lower = body.message.lower()
    if any(w in msg_lower for w in ["confirm", "yes", "available", "accept"]):
        reply = f"Hi {applicant['first_name']},\n\nThank you for confirming! Your interview is scheduled for March 5th. Please arrive 10 minutes early at the Vail Mountain Operations HQ. Bring a valid ID and any certification documents.\n\nSee you then!\n\nMountain Ops HR"
    elif any(w in msg_lower for w in ["reschedule", "different", "change", "another"]):
        reply = f"Hi {applicant['first_name']},\n\nAbsolutely! We have openings March 6th (9am-3pm) or March 7th (8am-2pm). Please let us know which works best and we'll update your calendar invite.\n\nMountain Ops HR"
    elif any(w in msg_lower for w in ["salary", "pay", "compensation", "wage"]):
        reply = f"Hi {applicant['first_name']},\n\nThe Ski Lift Operator position pays $22-26/hour based on experience, plus a full ski pass, equipment discounts, and access to resort amenities. We'll cover full details during your interview.\n\nMountain Ops HR"
    else:
        reply = f"Hi {applicant['first_name']},\n\nThank you for reaching out! A member of our team will follow up with you within 24 hours to address your question.\n\nMountain Ops HR"

    return {
        "applicant": name,
        "received_message": body.message,
        "ai_drafted_reply": reply,
        "sent_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


static_dir = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
