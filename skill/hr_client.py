#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from typing import Optional

BASE_URL = os.environ.get(
    "HR_APP_URL", "https://hr-resume-demo.dev.hyperplane.dev"
).rstrip("/")

SCORE_EMOJI = {
    "strong": "🟢",
    "consider": "🟡",
    "weak": "🟠",
    "reject": "🔴",
}

STATUS_EMOJI = {
    "new": "🆕",
    "reviewing": "🔍",
    "shortlisted": "⭐",
    "awaiting_reply": "✉️",
    "booked": "📅",
    "rejected": "❌",
    "hired": "✅",
}


def _get(path: str) -> dict:
    url = f"{BASE_URL}{path}"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.URLError as e:
        print(f"❌ Cannot reach HR app at `{BASE_URL}` — {e}")
        sys.exit(1)


def _post(path: str, data: dict) -> dict:
    url = f"{BASE_URL}{path}"
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        url, data=payload, method="POST", headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.URLError as e:
        print(f"❌ Request failed — {e}")
        sys.exit(1)


def _patch(path: str, data: dict) -> dict:
    url = f"{BASE_URL}{path}"
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        url, data=payload, method="PATCH", headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.URLError as e:
        print(f"❌ Request failed — {e}")
        sys.exit(1)


def _score_emoji(score: int) -> str:
    if score >= 75:
        return "🟢"
    elif score >= 55:
        return "🟡"
    elif score >= 35:
        return "🟠"
    return "🔴"


def _format_applicant_row(a: dict, rank: Optional[int] = None) -> str:
    sd = a.get("score_data")
    rd = a.get("response_data")
    status = a.get("status", "new")
    status_icon = STATUS_EMOJI.get(status, "•")
    name = f"{a['first_name']} {a['last_name']}"
    loc = f"{a.get('location', 'N/A')} ({a.get('distance_miles', 0):.0f}mi)"
    ski_years = sum(
        e.get("years", 0) for e in a["resume"]["experience"] if e.get("ski_related")
    )
    cert_count = len(a["resume"].get("certifications", []))

    if sd:
        score_str = f"{_score_emoji(sd['score'])} {sd['score']}/100"
    else:
        score_str = "—"

    if rd:
        response_str = f"💬 {rd['score']}/50 {rd['recommendation']}"
    else:
        response_str = "—"

    rank_str = f"{rank}." if rank else ""
    ski_str = f"{ski_years}yr ski" if ski_years > 0 else "no ski exp"
    cert_str = (
        f"{cert_count} cert{'s' if cert_count != 1 else ''}"
        if cert_count > 0
        else "no certs"
    )

    return f"| {rank_str} | {name} | {score_str} | {status_icon} {status} | {loc} | {ski_str} · {cert_str} | {response_str} |"


def cmd_list(args):
    applicants = _get("/api/applicants")
    job = _get("/api/job")

    filtered = applicants
    if args.status:
        filtered = [a for a in filtered if a["status"] == args.status]
    if args.min_score:
        filtered = [
            a
            for a in filtered
            if a.get("score_data", {}).get("score", 0) >= args.min_score
        ]
    if args.top:
        filtered = filtered[: args.top]

    title_suffix = ""
    if args.status:
        title_suffix = f" — Status: {args.status}"
    if args.min_score:
        title_suffix += f" — Score ≥{args.min_score}"
    if args.top:
        title_suffix += f" — Top {min(args.top, len(filtered))}"

    print(f"**🏔 {job['title']}{title_suffix}**")
    print(f"_Source: Paycom · {len(applicants)} total loaded_")
    print()

    if not filtered:
        print("_No candidates match the current filters._")
        print("Tip: run `score-all` to score candidates first, or widen your filter.")
        return

    print("| # | Name | Resume Score | Status | Location | Background | Response |")
    print("|---|------|-------------|--------|----------|------------|----------|")
    for i, a in enumerate(filtered, 1):
        print(_format_applicant_row(a, i))

    scored = sum(1 for a in filtered if a.get("score_data"))
    if not scored and filtered:
        print()
        print("_💡 No scores yet — run `score-all` to see rankings._")


def cmd_score_all(args):
    print("🤖 **Running AI scoring on all candidates...**")
    result = _post("/api/score/all", {})
    scored = result.get("scored", 0)
    promoted = result.get("auto_promoted", 0)
    threshold = result.get("threshold", 75)
    top_results = result.get("results", [])[:5]

    print()
    print(f"✅ **Scored {scored} candidates**")
    if promoted > 0:
        print(f"⬆️ {promoted} auto-promoted to **Reviewing** (score ≥ {threshold})")
    print()
    print("**Top 5:**")
    for r in top_results:
        emoji = _score_emoji(r["score"])
        print(f"• {emoji} {r['score']}/100 — {r.get('recommendation', '')}")


def cmd_score_one(args):
    applicants = _get("/api/applicants")

    target = None
    if args.id:
        target = next((a for a in applicants if a["id"] == args.id), None)
        if not target:
            print(f"❌ No applicant with ID `{args.id}`")
            return
    elif args.name:
        name_lower = args.name.lower()
        matches = [
            a
            for a in applicants
            if name_lower in f"{a['first_name']} {a['last_name']}".lower()
        ]
        if not matches:
            print(f"❌ No applicant matching `{args.name}`")
            return
        target = matches[0]

    if not target:
        print("❌ Provide --id or --name")
        return

    result = _post(f"/api/score/{target['id']}", {})
    name = f"{target['first_name']} {target['last_name']}"
    emoji = _score_emoji(result["score"])

    print(
        f"**📊 AI Score: {name} — {result['score']}/100** {emoji} {result['recommendation']}"
    )
    print()
    print("| Criterion | Score | Max |")
    print("|-----------|-------|-----|")
    for criterion, vals in result.get("breakdown", {}).items():
        print(f"| {criterion} | {vals['points']} | {vals['max']} |")
    print()
    for reason in result.get("reasons", []):
        print(reason)


def cmd_status(args):
    applicants = _get("/api/applicants")

    target = None
    if args.id:
        target = next((a for a in applicants if a["id"] == args.id), None)
    elif args.name:
        name_lower = args.name.lower()
        matches = [
            a
            for a in applicants
            if name_lower in f"{a['first_name']} {a['last_name']}".lower()
        ]
        if matches:
            target = matches[0]

    if not target:
        identifier = args.id or args.name or "unknown"
        print(f"❌ No applicant found matching `{identifier}`")
        print("Tip: use `search <name>` to find the correct ID.")
        return

    name = f"{target['first_name']} {target['last_name']}"
    status = target.get("status", "new")
    status_icon = STATUS_EMOJI.get(status, "•")
    sd = target.get("score_data")
    rd = target.get("response_data")
    ce = target.get("calendar_event")

    print(f"**👤 {name}** (`{target['id']}`)")
    print(
        f"📍 {target.get('location', 'N/A')} — {target.get('distance_miles', 0):.1f} miles from resort"
    )
    print(f"📌 Status: **{status_icon} {status.replace('_', ' ')}**")

    if sd:
        print(
            f"🎯 Resume Score: **{_score_emoji(sd['score'])} {sd['score']}/100** — {sd['recommendation']}"
        )
    else:
        print("🎯 Resume Score: _not yet scored_")

    if rd:
        print(f"💬 Response Score: **{rd['score']}/50** — {rd['recommendation']}")

    if target.get("email_sent_at"):
        print(f"📧 Invite sent: {target['email_sent_at'][:10]}")

    if ce:
        print(
            f"📅 Interview: **{ce['date']} at {ce['time']}** · {ce.get('location', '')}"
        )

    print(f"📅 Applied: {target.get('applied_date', 'N/A')}")
    print(f"📧 Email: {target.get('email', 'N/A')}")

    ski_years = sum(
        e.get("years", 0)
        for e in target["resume"]["experience"]
        if e.get("ski_related")
    )
    certs = target["resume"].get("certifications", [])
    if ski_years > 0:
        print(f"⛷️ {ski_years} year{'s' if ski_years > 1 else ''} ski resort experience")
    if certs:
        print(f"🏅 Certifications: {', '.join(certs[:3])}")


def cmd_email(args):
    applicants = _get("/api/applicants")
    ids = []

    if args.ids:
        ids = [i.strip() for i in args.ids.split(",")]
    elif args.status:
        filtered = [a for a in applicants if a["status"] == args.status]
        if args.top:
            filtered = filtered[: args.top]
        ids = [a["id"] for a in filtered]

    if not ids:
        print(
            "❌ No candidates selected. Use `--ids PAY-001,PAY-002` or `--status reviewing`."
        )
        return

    if args.preview:
        print(
            f"**📋 Email Preview — {len(ids)} candidate{'s' if len(ids) > 1 else ''}**"
        )
        previews = _post("/api/email/preview", {"applicant_ids": ids})
        for p in previews.get("previews", []):
            print(f"\n---\n**To:** {p['name']} ({p['email']})")
            print(f"**Subject:** {p['subject']}")
            if p.get("questions"):
                print(f"**Questions selected for {p['name'].split()[0]}:**")
                for i, q in enumerate(p["questions"], 1):
                    print(f"{i}. {q}")
        return

    result = _post("/api/bulk", {"applicant_ids": ids, "action": "send_invite"})
    processed = result.get("processed", 0)
    mode = (
        result.get("results", [{}])[0].get("mode", "mock")
        if result.get("results")
        else "mock"
    )

    print(
        f"**📧 Interview Invites Sent — {processed} candidate{'s' if processed > 1 else ''}**"
    )
    print(f"Mode: {'⚗️ Mock' if mode == 'mock' else '📤 Real'}")
    print()
    print("| Candidate | Email | Action |")
    print("|-----------|-------|--------|")
    for r in result.get("results", []):
        print(f"| ✅ {r['name']} | {r.get('email', '—')} | invite sent |")
    print()
    print(f"Candidates moved to **✉️ Awaiting Reply**.")
    if mode == "mock":
        print("_Mock responses will arrive in ~5 seconds in the dashboard._")


def cmd_book(args):
    applicants = _get("/api/applicants")
    ids = []

    if args.ids:
        ids = [i.strip() for i in args.ids.split(",")]
    elif args.status:
        filtered = [a for a in applicants if a["status"] == args.status]
        if args.top:
            filtered = filtered[: args.top]
        ids = [a["id"] for a in filtered]

    if not ids:
        print(
            "❌ No candidates selected. Use `--ids PAY-001,PAY-002` or `--status awaiting_reply`."
        )
        return

    result = _post("/api/bulk", {"applicant_ids": ids, "action": "book_interview"})
    processed = result.get("processed", 0)

    print(
        f"**📅 Interviews Booked — {processed} candidate{'s' if processed > 1 else ''}**"
    )
    print()
    print("| Candidate | Date | Time | Location |")
    print("|-----------|------|------|----------|")
    for r in result.get("results", []):
        ce = r.get("calendar_event", {})
        print(
            f"| {r['name']} | {ce.get('date', '—')} | {ce.get('time', '—')} | {ce.get('location', '—')} |"
        )
    print()
    print("Candidates moved to **📅 Booked**.")


def cmd_summary(args):
    applicants = _get("/api/applicants")
    job = _get("/api/job")

    by_status: dict = {}
    for a in applicants:
        s = a.get("status", "new")
        by_status.setdefault(s, []).append(a)

    all_scored = [a for a in applicants if a.get("score_data")]
    top = all_scored[0] if all_scored else None

    print(f"**🏔 {job['title']} — Pipeline Summary**")
    print(f"_{job.get('location', '')} · {job.get('season', '')}_")
    print()
    print("| Stage | Count | Top Score |")
    print("|-------|-------|-----------|")

    order = [
        "new",
        "reviewing",
        "shortlisted",
        "awaiting_reply",
        "booked",
        "hired",
        "rejected",
    ]
    for status in order:
        group = by_status.get(status, [])
        if not group and status not in ("hired", "rejected"):
            continue
        icon = STATUS_EMOJI.get(status, "•")
        scored_in_group = [a for a in group if a.get("score_data")]
        top_score = max(
            (a["score_data"]["score"] for a in scored_in_group), default=None
        )
        top_str = f"{_score_emoji(top_score)} {top_score}/100" if top_score else "—"
        print(
            f"| {icon} {status.replace('_', ' ').title()} | {len(group)} | {top_str} |"
        )

    print()
    total = job.get("applicant_count", len(applicants))
    scored_count = len(all_scored)
    print(
        f"**{total} total applicants** · **{len(applicants)} loaded** · **{scored_count} scored**"
    )
    if top:
        top_name = f"{top['first_name']} {top['last_name']}"
        top_score = top["score_data"]["score"]
        print(
            f"_Top candidate: {top_name} ({_score_emoji(top_score)} {top_score}/100) — {top.get('location', '')}_"
        )


def cmd_refresh(args):
    result = _post("/api/paycom/refresh", {})
    count = result.get("applicant_count", 0)
    print(f"🔄 **Paycom Sync Complete**")
    print(f"Pulled **{count} applicants** for Ski Lift Operator.")
    print("All scores and statuses reset. Ready to run AI scoring.")


def cmd_search(args):
    applicants = _get("/api/applicants")
    query = args.query.lower()
    matches = [
        a for a in applicants if query in f"{a['first_name']} {a['last_name']}".lower()
    ]

    if not matches:
        print(f"❌ No candidates matching `{args.query}`")
        return

    print(f'**🔍 Search results for "{args.query}" — {len(matches)} found**')
    print()
    print("| Name | ID | Score | Status | Location |")
    print("|------|-----|-------|--------|----------|")
    for a in matches:
        sd = a.get("score_data")
        score_str = f"{_score_emoji(sd['score'])} {sd['score']}" if sd else "—"
        status_icon = STATUS_EMOJI.get(a["status"], "•")
        print(
            f"| {a['first_name']} {a['last_name']} | `{a['id']}` | {score_str} | {status_icon} {a['status']} | {a.get('location', '—')} |"
        )


def cmd_digest(args):
    applicants = _get("/api/applicants")
    job = _get("/api/job")

    by_status: dict = {}
    for a in applicants:
        s = a.get("status", "new")
        by_status.setdefault(s, []).append(a)

    new_count = len(by_status.get("new", []))
    reviewing = by_status.get("reviewing", [])
    awaiting = by_status.get("awaiting_reply", [])
    booked = by_status.get("booked", [])
    unscored_reviewing = [a for a in reviewing if not a.get("score_data")]

    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"**☀️ Daily HR Digest — {job['title']}**")
    print(f"_Generated: {today}_")
    print()
    print(f"📥 **In New queue:** {new_count} candidates")
    print(f"🔍 **In Reviewing:** {len(reviewing)} candidates")
    print(f"✉️ **Awaiting reply:** {len(awaiting)} candidates")
    print(f"📅 **Booked for interview:** {len(booked)}")
    print()

    actions = []
    if new_count > 0:
        actions.append(f"• {new_count} new candidates to score — run `score-all`")
    if unscored_reviewing:
        actions.append(
            f"• {len(unscored_reviewing)} reviewing candidates not yet scored"
        )
    if len(reviewing) > 0 and len(awaiting) == 0:
        actions.append(
            f"• {len(reviewing)} reviewing candidates not yet contacted — run `email --status reviewing`"
        )
    if awaiting:
        actions.append(
            f"• {len(awaiting)} candidates awaiting reply — consider `book --status awaiting_reply`"
        )

    if actions:
        print("**⚡ Action needed:**")
        for a in actions:
            print(a)
    else:
        print("✅ _Pipeline looks good — no immediate actions needed._")


def main():
    parser = argparse.ArgumentParser(
        prog="hr_client", description="HR Resume Processor — Kaji Skill CLI"
    )
    subparsers = parser.add_subparsers(dest="command")

    p_list = subparsers.add_parser("list", help="List candidates")
    p_list.add_argument("--status", help="Filter by status")
    p_list.add_argument("--min-score", type=int, help="Minimum AI score")
    p_list.add_argument("--top", type=int, help="Limit to top N")

    p_score_all = subparsers.add_parser("score-all", help="Score all candidates")

    p_score = subparsers.add_parser("score", help="Score a specific candidate")
    p_score.add_argument("id", nargs="?", help="Applicant ID (e.g. PAY-0003)")
    p_score.add_argument("--name", help="Candidate name (fuzzy match)")

    p_status = subparsers.add_parser("status", help="Check candidate status")
    p_status.add_argument("id", nargs="?", help="Applicant ID")
    p_status.add_argument("--name", help="Candidate name")

    p_email = subparsers.add_parser("email", help="Send interview invites")
    p_email.add_argument(
        "ids", nargs="?", help="Comma-separated IDs (e.g. PAY-001,PAY-002)"
    )
    p_email.add_argument("--status", help="Email all in this status")
    p_email.add_argument("--top", type=int, help="Limit to top N in status")
    p_email.add_argument(
        "--preview", action="store_true", help="Preview emails without sending"
    )

    p_book = subparsers.add_parser("book", help="Book interviews")
    p_book.add_argument("ids", nargs="?", help="Comma-separated IDs")
    p_book.add_argument("--status", help="Book all in this status")
    p_book.add_argument("--top", type=int, help="Limit to top N")

    subparsers.add_parser("summary", help="Pipeline overview")
    subparsers.add_parser("refresh", help="Sync from Paycom")
    subparsers.add_parser("digest", help="Daily digest")

    p_search = subparsers.add_parser("search", help="Search candidates by name")
    p_search.add_argument("query", help="Name to search for")

    args = parser.parse_args()

    dispatch = {
        "list": cmd_list,
        "score-all": cmd_score_all,
        "score": cmd_score_one,
        "status": cmd_status,
        "email": cmd_email,
        "book": cmd_book,
        "summary": cmd_summary,
        "refresh": cmd_refresh,
        "digest": cmd_digest,
        "search": cmd_search,
    }

    if not args.command:
        parser.print_help()
        return

    fn = dispatch.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
