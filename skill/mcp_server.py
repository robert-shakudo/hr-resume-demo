#!/usr/bin/env python3
"""
HR Resume Processor — MCP Server
Wraps the HR app REST API as MCP tools for Kaji.
Start: python mcp_server.py  (stdio transport, used by opencode)
"""
import json
import os
import urllib.request
import urllib.error
from typing import Optional

from mcp.server.fastmcp import FastMCP

BASE_URL = os.environ.get("HR_APP_URL", "https://hr-resume-demo.dev.hyperplane.dev").rstrip("/")

mcp = FastMCP(
    "hr-resume-processor",
    instructions=(
        "HR Resume Processor for Ski Lift Operator hiring. "
        "Use these tools to list candidates, run AI scoring, send interview invites, "
        "book interviews, and manage the full hiring pipeline. "
        "Always call hr_pipeline_summary first to understand the current state."
    ),
)


def _get(path: str) -> dict:
    with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=15) as r:
        return json.loads(r.read())


def _post(path: str, data: dict) -> dict:
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE_URL}{path}", data=payload, method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _patch(path: str, data: dict) -> dict:
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE_URL}{path}", data=payload, method="PATCH",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def _score_icon(score: int) -> str:
    if score >= 75: return "🟢"
    if score >= 55: return "🟡"
    if score >= 35: return "🟠"
    return "🔴"


def _status_icon(status: str) -> str:
    return {"new": "🆕", "reviewing": "🔍", "shortlisted": "⭐",
            "awaiting_reply": "✉️", "booked": "📅", "rejected": "❌", "hired": "✅"}.get(status, "•")


@mcp.tool()
def hr_list_candidates(
    status: Optional[str] = None,
    min_score: Optional[int] = None,
    top: Optional[int] = None,
) -> str:
    """
    List HR candidates from the pipeline. Filter by status, minimum AI score, or limit to top N.
    Valid statuses: new, reviewing, shortlisted, awaiting_reply, booked, rejected, hired.
    Returns a ranked Mattermost-formatted table.
    """
    applicants = _get("/api/applicants")
    job = _get("/api/job")

    if status:
        applicants = [a for a in applicants if a["status"] == status]
    if min_score:
        applicants = [a for a in applicants if a.get("score_data", {}).get("score", 0) >= min_score]
    if top:
        applicants = applicants[:top]

    if not applicants:
        return "No candidates match the current filter. Try widening status or score filter, or run `hr_score_all` first."

    lines = [f"**🏔 {job['title']} — {len(applicants)} candidates**\n"]
    lines.append("| # | Name | Score | Response | Status | Location |")
    lines.append("|---|------|-------|----------|--------|----------|")
    for i, a in enumerate(applicants, 1):
        sd = a.get("score_data")
        rd = a.get("response_data")
        score_str = f"{_score_icon(sd['score'])} {sd['score']}/100" if sd else "—"
        resp_str = f"💬 {rd['score']}/50 {rd['recommendation']}" if rd else "—"
        loc = f"{a.get('location', '?')} ({a.get('distance_miles', 0):.0f}mi)"
        status_str = f"{_status_icon(a['status'])} {a['status'].replace('_', ' ')}"
        lines.append(f"| {i} | {a['first_name']} {a['last_name']} | {score_str} | {resp_str} | {status_str} | {loc} |")

    if not any(a.get("score_data") for a in applicants):
        lines.append("\n_💡 No scores yet — call `hr_score_all` to run AI scoring._")
    return "\n".join(lines)


@mcp.tool()
def hr_get_candidate(applicant_id: str) -> str:
    """
    Get detailed profile for a specific candidate by their Paycom ID (e.g. PAY-0003).
    Returns full resume details, AI score breakdown, response score, and calendar event if booked.
    """
    try:
        a = _get(f"/api/applicants/{applicant_id}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"❌ Applicant `{applicant_id}` not found. Use `hr_search_candidates` to find the correct ID."
        raise

    sd = a.get("score_data")
    rd = a.get("response_data")
    ce = a.get("calendar_event")
    ski_years = sum(e.get("years", 0) for e in a["resume"]["experience"] if e.get("ski_related"))
    certs = a["resume"].get("certifications", [])

    lines = [
        f"**👤 {a['first_name']} {a['last_name']}** (`{a['id']}`)",
        f"📍 {a.get('location', 'N/A')} — {a.get('distance_miles', 0):.1f} miles from resort",
        f"📌 Status: **{_status_icon(a['status'])} {a['status'].replace('_', ' ')}**",
        f"📅 Applied: {a.get('applied_date', 'N/A')}",
        f"📧 {a.get('email', 'N/A')}",
    ]
    if ski_years > 0:
        lines.append(f"⛷️ {ski_years} year{'s' if ski_years > 1 else ''} ski resort experience")
    if certs:
        lines.append(f"🏅 Certs: {', '.join(certs[:4])}")
    if sd:
        lines.append(f"\n**Resume Score:** {_score_icon(sd['score'])} **{sd['score']}/100** — {sd['recommendation']}")
        for criterion, vals in sd.get("breakdown", {}).items():
            lines.append(f"  • {criterion}: {vals['points']}/{vals['max']}")
        for reason in sd.get("reasons", []):
            lines.append(f"  {reason}")
    if rd:
        lines.append(f"\n**Response Score:** 💬 **{rd['score']}/50** — {rd['recommendation']}")
        lines.append(f"  \"{rd['text'][:200]}{'...' if len(rd['text']) > 200 else ''}\"")
    if ce:
        lines.append(f"\n**📅 Interview Booked:** {ce['date']} at {ce['time']} · {ce.get('location', '')}")
    return "\n".join(lines)


@mcp.tool()
def hr_search_candidates(query: str) -> str:
    """
    Search candidates by name (partial match). Returns IDs, scores, and status.
    Use this to find the correct applicant_id before calling other tools.
    """
    applicants = _get("/api/applicants")
    q = query.lower()
    matches = [a for a in applicants if q in f"{a['first_name']} {a['last_name']}".lower()]

    if not matches:
        return f"No candidates found matching `{query}`."

    lines = [f"**🔍 Search results for \"{query}\" — {len(matches)} found**\n"]
    lines.append("| Name | ID | Score | Status |")
    lines.append("|------|-----|-------|--------|")
    for a in matches:
        sd = a.get("score_data")
        score_str = f"{_score_icon(sd['score'])} {sd['score']}" if sd else "—"
        lines.append(f"| {a['first_name']} {a['last_name']} | `{a['id']}` | {score_str} | {_status_icon(a['status'])} {a['status']} |")
    return "\n".join(lines)


@mcp.tool()
def hr_score_all() -> str:
    """
    Run AI scoring on ALL candidates. Scores against Ski Lift Operator criteria
    (ski experience 35pts, certifications 25pts, availability 20pts, proximity 15pts, physical 5pts).
    Candidates scoring above the auto-promote threshold are automatically moved to 'reviewing'.
    Returns a summary with auto-promoted count and top 5 scores.
    """
    result = _post("/api/score/all", {})
    scored = result.get("scored", 0)
    promoted = result.get("auto_promoted", 0)
    threshold = result.get("threshold", 75)
    top = result.get("results", [])[:5]

    lines = [f"✅ **AI Scoring Complete — {scored} candidates scored**"]
    if promoted > 0:
        lines.append(f"⬆️ **{promoted} auto-promoted** to Reviewing (score ≥ {threshold})")
    lines.append("\n**Top 5:**")
    for r in top:
        lines.append(f"• {_score_icon(r['score'])} {r['score']}/100 — {r.get('recommendation', '')}")
    lines.append(f"\nUse `hr_list_candidates(status='reviewing')` to see promoted candidates.")
    return "\n".join(lines)


@mcp.tool()
def hr_score_candidate(applicant_id: str) -> str:
    """
    Run AI scoring on a single candidate. Returns the full score breakdown with reasoning.
    """
    try:
        result = _post(f"/api/score/{applicant_id}", {})
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"❌ Applicant `{applicant_id}` not found."
        raise

    lines = [
        f"**📊 AI Score: {_score_icon(result['score'])} {result['score']}/100 — {result['recommendation']}**",
        "",
        "| Criterion | Score | Max |",
        "|-----------|-------|-----|",
    ]
    for criterion, vals in result.get("breakdown", {}).items():
        lines.append(f"| {criterion} | {vals['points']} | {vals['max']} |")
    lines.append("")
    for reason in result.get("reasons", []):
        lines.append(reason)
    return "\n".join(lines)


@mcp.tool()
def hr_send_invites(
    applicant_ids: list[str],
    preview_only: bool = False,
) -> str:
    """
    Send personalized interview invite emails to candidates.
    Each email is personalized with relevant interview questions based on their background.
    Set preview_only=True to see email content without sending.
    Candidates are moved to 'awaiting_reply'. In mock mode, responses arrive in ~5 seconds.
    """
    if preview_only:
        result = _post("/api/email/preview", {"applicant_ids": applicant_ids})
        previews = result.get("previews", [])
        lines = [f"**📋 Email Preview — {len(previews)} recipient(s)**\n"]
        for p in previews[:3]:
            lines.append(f"**To:** {p['name']} ({p['email']})")
            lines.append(f"**Subject:** {p['subject']}")
            if p.get("questions"):
                lines.append("**Questions for this candidate:**")
                for i, q in enumerate(p["questions"], 1):
                    lines.append(f"{i}. {q}")
            lines.append(f"**Body preview:** {p['body'][:200]}...")
            lines.append("---")
        return "\n".join(lines)

    result = _post("/api/bulk", {"applicant_ids": applicant_ids, "action": "send_invite"})
    processed = result.get("processed", 0)
    mode = result.get("results", [{}])[0].get("mode", "mock") if result.get("results") else "mock"

    lines = [f"**📧 Interview Invites Sent — {processed} candidate(s)**"]
    lines.append(f"Mode: {'⚗️ Mock (test email)' if mode == 'mock' else '📤 Real (actual emails)'}")
    lines.append("")
    lines.append("| Candidate | Action |")
    lines.append("|-----------|--------|")
    for r in result.get("results", []):
        lines.append(f"| {r['name']} | ✅ invite sent |")
    lines.append(f"\nCandidates moved to **✉️ Awaiting Reply**.")
    if mode == "mock":
        lines.append("_Mock responses will arrive in ~5 seconds in the dashboard._")
    return "\n".join(lines)


@mcp.tool()
def hr_book_interviews(applicant_ids: list[str]) -> str:
    """
    Book interview slots for candidates. Creates Google Calendar events and moves
    candidates to 'booked' status with date/time/location details.
    """
    result = _post("/api/bulk", {"applicant_ids": applicant_ids, "action": "book_interview"})
    processed = result.get("processed", 0)

    lines = [f"**📅 Interviews Booked — {processed} candidate(s)**", ""]
    lines.append("| Candidate | Date | Time | Location |")
    lines.append("|-----------|------|------|----------|")
    for r in result.get("results", []):
        ce = r.get("calendar_event", {})
        lines.append(f"| {r['name']} | {ce.get('date', '—')} | {ce.get('time', '—')} | {ce.get('location', '—')} |")
    lines.append("\nCandidates moved to **📅 Booked**.")
    return "\n".join(lines)


@mcp.tool()
def hr_update_status(applicant_id: str, status: str) -> str:
    """
    Manually update a candidate's pipeline status.
    Valid statuses: new, reviewing, shortlisted, awaiting_reply, booked, rejected, hired.
    """
    valid = {"new", "reviewing", "shortlisted", "awaiting_reply", "booked", "rejected", "hired"}
    if status not in valid:
        return f"❌ Invalid status `{status}`. Valid: {', '.join(sorted(valid))}"
    try:
        result = _patch(f"/api/applicants/{applicant_id}/status", {"status": status})
        return f"✅ {applicant_id} status updated to **{_status_icon(status)} {status}**"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"❌ Applicant `{applicant_id}` not found."
        raise


@mcp.tool()
def hr_pipeline_summary() -> str:
    """
    Get a snapshot of the full hiring pipeline — candidate counts by stage,
    top score, and recommended next actions. Always call this first.
    """
    applicants = _get("/api/applicants")
    job = _get("/api/job")

    by_status: dict = {}
    for a in applicants:
        by_status.setdefault(a.get("status", "new"), []).append(a)

    scored = [a for a in applicants if a.get("score_data")]
    top = scored[0] if scored else None

    lines = [
        f"**🏔 {job['title']} — Pipeline Summary**",
        f"_{job.get('location', '')} · {job.get('season', '')}_",
        "",
        "| Stage | Count | Top Score |",
        "|-------|-------|-----------|",
    ]
    for status in ["new", "reviewing", "shortlisted", "awaiting_reply", "booked", "hired", "rejected"]:
        group = by_status.get(status, [])
        if not group and status not in ("hired", "rejected"):
            continue
        scored_g = [a for a in group if a.get("score_data")]
        top_score = max((a["score_data"]["score"] for a in scored_g), default=None)
        top_str = f"{_score_icon(top_score)} {top_score}/100" if top_score else "—"
        icon = _status_icon(status)
        lines.append(f"| {icon} {status.replace('_', ' ').title()} | {len(group)} | {top_str} |")

    lines.append("")
    lines.append(f"**{job.get('applicant_count', len(applicants))} total · {len(applicants)} loaded · {len(scored)} scored**")
    if top:
        lines.append(f"_Top: {top['first_name']} {top['last_name']} ({_score_icon(top['score_data']['score'])} {top['score_data']['score']}/100) — {top.get('location', '')}_")

    actions = []
    new_unscored = [a for a in by_status.get("new", []) if not a.get("score_data")]
    if new_unscored:
        actions.append(f"• {len(new_unscored)} unscored candidates in New → call `hr_score_all`")
    reviewing = by_status.get("reviewing", [])
    if reviewing and not by_status.get("awaiting_reply"):
        actions.append(f"• {len(reviewing)} candidates in Reviewing not yet invited → call `hr_send_invites`")
    awaiting = by_status.get("awaiting_reply", [])
    responded = [a for a in awaiting if a.get("response_data")]
    if responded:
        actions.append(f"• {len(responded)} candidates replied → review and call `hr_book_interviews`")
    if actions:
        lines.append("\n**⚡ Suggested next steps:**")
        lines.extend(actions)
    return "\n".join(lines)


@mcp.tool()
def hr_refresh_paycom() -> str:
    """
    Sync/reset all applicant data from Paycom. Clears all scores and statuses,
    reloads the original 30 ski lift operator applicants. Use to start a fresh demo.
    """
    result = _post("/api/paycom/refresh", {})
    return (
        f"🔄 **Paycom Sync Complete**\n"
        f"Pulled **{result.get('applicant_count', 0)} applicants** for Ski Lift Operator.\n"
        f"All scores and statuses reset. Call `hr_score_all` to begin processing."
    )


@mcp.tool()
def hr_get_settings() -> str:
    """
    Get current HR app settings: AI scoring thresholds, email mode (mock/real),
    email template, and interview questions.
    """
    s = _get("/api/settings")
    scoring = s.get("scoring", {})
    email = s.get("email", {})
    questions = s.get("questions", [])

    lines = [
        "**⚙️ HR App Settings**",
        "",
        f"**AI Scoring Thresholds:**",
        f"  • Auto-promote to Reviewing: ≥ {scoring.get('auto_promote_threshold', 75)} pts",
        f"  • Strong Hire badge: ≥ {scoring.get('strong_hire_threshold', 75)} pts",
        f"  • Consider badge: ≥ {scoring.get('consider_threshold', 55)} pts",
        "",
        f"**Email Mode:** {'⚗️ Mock' if email.get('mode') == 'mock' else '📤 Real'}",
        f"**Subject:** {email.get('subject', '')}",
        "",
        f"**Interview Questions ({len(questions)}):**",
    ]
    for i, q in enumerate(questions, 1):
        lines.append(f"{i}. {q}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
