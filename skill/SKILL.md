---
name: hr-resume-processor
description: "Chat-native HR assistant for resume processing and hiring pipelines. View candidates, run AI scoring, send personalized interview invites, book interviews, and manage applicant state — all from a Mattermost thread. Wraps the HR Resume Processor app API. Use when asked about candidates, scores, hiring pipeline, or interview scheduling."
license: MIT
compatibility: opencode
metadata:
  author: shakudo
  version: "1.0"
  category: hr
  tags:
    - hr
    - hiring
    - resume
    - paycom
    - interviews
    - candidates
---

# HR Resume Processor Skill

Chat-native access to the full HR hiring pipeline. Same backend as the dashboard — Mattermost is the interface.

## When to Use This Skill

Activate when the user asks anything related to:
- Viewing, filtering, or ranking candidates
- Running or checking AI scores
- Sending interview invites
- Booking or checking interview slots
- Checking applicant status or pipeline state
- Syncing or refreshing from Paycom
- Getting a hiring summary or digest

**Trigger phrases:** "show candidates", "top applicants", "score resume", "email shortlisted", "book interview", "who's in reviewing", "sync paycom", "hiring status", "applicant pipeline"

---

## Configuration

### Environment Variable

```bash
HR_APP_URL=https://hr-resume-demo.dev.hyperplane.dev
```

Set in `.env` or export before running:

```bash
export HR_APP_URL=https://hr-resume-demo.dev.hyperplane.dev
```

### Load Credentials

```bash
source /root/gitrepos/.claude/skills/hr-resume-processor/.env
```

---

## Core Commands

All commands use the `hr_client.py` script in this skill directory.

```bash
python skill/hr_client.py <command> [options]
```

---

### 1. List Candidates

Show all candidates, optionally filtered and sorted.

```bash
# Top 10 by AI score
python skill/hr_client.py list --top 10

# Filter by status
python skill/hr_client.py list --status reviewing
python skill/hr_client.py list --status awaiting_reply
python skill/hr_client.py list --status booked

# Filter by minimum score
python skill/hr_client.py list --min-score 75

# Combined
python skill/hr_client.py list --status reviewing --min-score 75 --top 10
```

**Valid statuses:** `new`, `reviewing`, `shortlisted`, `awaiting_reply`, `booked`, `rejected`, `hired`

**Mattermost output:**
```
**🏔 Ski Lift Operator — Top Candidates**
| Rank | Name | Score | Status | Location | Ski Exp | Certs |
|------|------|-------|--------|----------|---------|-------|
| 1 | Lane Young | 🟢 97/100 | reviewing | Vail, CO (2.5mi) | 7yr | OSHA 30, ANSI |
| 2 | Alex Rivera | 🟢 95/100 | reviewing | Vail, CO (2.1mi) | 8yr | OSHA 30, ANSI |
...
```

---

### 2. Score Candidates

Run AI scoring on all candidates or a specific one.

```bash
# Score all (auto-promotes top scorers to "reviewing")
python skill/hr_client.py score-all

# Score a specific candidate by ID
python skill/hr_client.py score PAY-0003

# Score by name (fuzzy match)
python skill/hr_client.py score --name "Alex Rivera"
```

**Mattermost output (single candidate):**
```
**📊 AI Score: Alex Rivera — 95/100** 🟢 Strong Hire

| Criterion | Score | Max |
|-----------|-------|-----|
| Ski Resort Experience | 35 | 35 |
| Safety Certifications | 25 | 25 |
| Availability | 20 | 20 |
| Proximity | 13 | 15 |
| Physical/Outdoor | 5 | 5 |

✅ Direct lift operator experience (8 years)
✅ Strong safety certification suite (OSHA 30, ANSI/ASME)
✅ Full availability (weekends, holidays, early AM)
✅ Very close to resort (2.1 miles)
```

---

### 3. Get Applicant Status

Check where a specific candidate is in the pipeline.

```bash
python skill/hr_client.py status PAY-0003
python skill/hr_client.py status --name "Jane Doe"
```

**Mattermost output:**
```
**👤 Alex Rivera** (PAY-0003)
📍 Vail, CO — 2.1 miles from resort
📌 Status: **reviewing**
🎯 Resume Score: 95/100 (Strong Hire)
📅 Applied: 2026-01-15
📧 Email: alex.rivera@email.com
```

---

### 4. Send Interview Invites

Email shortlisted candidates with personalized invites including relevant interview questions.

```bash
# Email specific candidates by ID
python skill/hr_client.py email PAY-0003,PAY-0005,PAY-0001

# Email all candidates in a status
python skill/hr_client.py email --status reviewing --top 5

# Preview emails first (no send)
python skill/hr_client.py email PAY-0003 --preview
```

**Mattermost output:**
```
**📧 Interview Invites Sent — 5 candidates**
Mode: Mock (test@demo.com)

| Candidate | Score | Email |
|-----------|-------|-------|
| ✅ Lane Young | 97 | lane.young@email.com |
| ✅ Alex Rivera | 95 | alex.rivera@email.com |
| ✅ Cameron Wilson | 93 | cameron.wilson@email.com |
| ✅ Avery White | 91 | avery.white@email.com |
| ✅ Sam Rodriguez | 89 | sam.rodriguez@email.com |

Candidates moved to **Awaiting Reply**. Mock responses in ~5s.
```

---

### 5. Book Interviews

Schedule interview slots for candidates.

```bash
# Book by ID
python skill/hr_client.py book PAY-0003,PAY-0005

# Book all awaiting-reply candidates
python skill/hr_client.py book --status awaiting_reply
```

**Mattermost output:**
```
**📅 Interviews Booked — 3 candidates**

| Candidate | Date | Time | Location |
|-----------|------|------|----------|
| Lane Young | 2026-03-05 | 08:00 | Vail Ops HQ, Room A2 |
| Alex Rivera | 2026-03-05 | 09:00 | Vail Ops HQ, Room A2 |
| Cameron Wilson | 2026-03-05 | 10:00 | Vail Ops HQ, Room A2 |

Candidates moved to **Booked**.
```

---

### 6. Pipeline Summary

Get a snapshot of the full hiring pipeline.

```bash
python skill/hr_client.py summary
```

**Mattermost output:**
```
**🏔 Ski Lift Operator — Pipeline Summary**
_Vail Mountain · Winter 2025-2026_

| Stage | Count | Top Score |
|-------|-------|-----------|
| 🆕 New | 18 | — |
| 🔍 Reviewing | 8 | 97/100 |
| ✉️ Awaiting Reply | 4 | 95/100 |
| 📅 Booked | 2 | 97/100 |
| ✅ Hired | 0 | — |
| ❌ Rejected | 3 | — |

**170 total applicants** · **30 loaded** · **12 scored**
_Top candidate: Lane Young (97/100) — Vail, CO_
```

---

### 7. Sync Paycom

Refresh applicant data from Paycom (resets all statuses and scores).

```bash
python skill/hr_client.py refresh
```

**Mattermost output:**
```
🔄 **Paycom Sync Complete**
Pulled **30 applicants** for Ski Lift Operator.
All scores and statuses reset. Ready to run AI scoring.
```

---

### 8. Search Candidates

Find a candidate by name.

```bash
python skill/hr_client.py search "Jake Morrison"
python skill/hr_client.py search "Jake"
```

---

## Workflow: Full Hiring Pipeline

Execute the complete pipeline in one session:

```bash
# Step 1: Sync from Paycom
python skill/hr_client.py refresh

# Step 2: Score all candidates
python skill/hr_client.py score-all

# Step 3: Review top candidates
python skill/hr_client.py list --status reviewing --top 10

# Step 4: Send invites to top 5
python skill/hr_client.py email --status reviewing --top 5

# Step 5: Check who responded (after 5s in mock mode)
python skill/hr_client.py list --status awaiting_reply

# Step 6: Book top responders
python skill/hr_client.py book --status awaiting_reply

# Step 7: Get pipeline summary
python skill/hr_client.py summary
```

---

## Workflow: Auto-Score New Applicant (Webhook Trigger)

When Paycom fires a new applicant webhook, Kaji can:

1. Score the new applicant automatically
2. Post a notification to `#hr-hiring` channel

**Trigger payload from Paycom:**
```json
{
  "event": "new_applicant",
  "applicant_id": "PAY-0031",
  "job": "Ski Lift Operator"
}
```

**Kaji auto-response:**
```bash
# Score the new applicant
python skill/hr_client.py score PAY-0031

# Post to channel (using Mattermost MCP)
# mattermost_post_message(channel_id="hr-hiring", message="...")
```

**Channel notification format:**
```
🆕 **New Applicant: Jake Morrison** for Ski Lift Operator
📊 AI Score: **87/100** 🟢 Strong Hire
📍 Breckenridge, CO (4.2 miles)
⛷️ 3yr ski resort experience · OSHA 10 · First Aid/CPR

[View in Dashboard](https://hr-resume-demo.dev.hyperplane.dev) | Reply to email, book, or reject
```

---

## Daily Digest Workflow

Post a morning summary to `#hr-hiring`:

```bash
python skill/hr_client.py digest
```

**Output:**
```
**☀️ Daily HR Digest — Ski Lift Operator**
_Generated: 2026-03-01 09:00_

📥 **New since yesterday:** 3 applicants
🤖 **Scored today:** 8 candidates
📧 **Awaiting reply:** 4 candidates
📅 **Interviews this week:** 2 scheduled

**Action needed:**
- 4 candidates in "Reviewing" not yet contacted
- 2 interviews tomorrow (Lane Young 9am, Alex Rivera 10am)

Run `score-all` to process pending candidates.
```

---

## Response Formatting Reference

All commands output Mattermost-compatible markdown. Key patterns:

| Element | Format |
|---------|--------|
| Strong Hire | `🟢 XX/100` |
| Consider | `🟡 XX/100` |
| Weak/Reject | `🔴 XX/100` |
| Status: reviewing | `🔍 reviewing` |
| Status: awaiting_reply | `✉️ awaiting_reply` |
| Status: booked | `📅 booked` |
| Status: hired | `✅ hired` |
| Status: rejected | `❌ rejected` |

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `Connection refused` | HR app not running | Check `HR_APP_URL` env var |
| `404 Applicant not found` | Wrong ID | Use `search` command to find correct ID |
| `No candidates match filter` | Filter too narrow | Widen status or score filter |
| `Score data not available` | Not yet scored | Run `score-all` first |

---

## Example Conversations

**"Show me the top 10 candidates"**
→ `python skill/hr_client.py list --top 10`

**"What's the status of Alex Rivera?"**
→ `python skill/hr_client.py status --name "Alex Rivera"`

**"Email all reviewing candidates"**
→ `python skill/hr_client.py email --status reviewing`

**"Book interviews for everyone who replied"**
→ `python skill/hr_client.py book --status awaiting_reply`

**"Score all the new applicants"**
→ `python skill/hr_client.py score-all`

**"Give me a hiring summary"**
→ `python skill/hr_client.py summary`

**"Refresh from Paycom"**
→ `python skill/hr_client.py refresh`

---

## MCP Tools Reference

When the MCP server is registered, Kaji calls these tools directly (no shell commands needed):

| Tool | Description |
|------|-------------|
| `hr_pipeline_summary` | Full pipeline snapshot — call this first |
| `hr_list_candidates` | List/filter candidates by status, score, or count |
| `hr_get_candidate` | Full profile for a specific applicant ID |
| `hr_search_candidates` | Find candidates by name |
| `hr_score_all` | Run AI scoring on all candidates, auto-promote top |
| `hr_score_candidate` | Score a single candidate by ID |
| `hr_send_invites` | Send personalized invite emails (mock or real) |
| `hr_book_interviews` | Book calendar slots, move to Booked |
| `hr_update_status` | Manually move a candidate to any status |
| `hr_refresh_paycom` | Reset all data from Paycom |
| `hr_get_settings` | View scoring thresholds, email mode, questions |

### Register MCP server in opencode config

Add to your `~/.config/opencode/opencode.json` under `"mcp"`:

```json
{
  "mcp": {
    "hr-resume-processor": {
      "type": "local",
      "command": ["python", "/root/gitrepos/.claude/skills/hr-resume-processor/mcp_server.py"],
      "enabled": true,
      "environment": {
        "HR_APP_URL": "https://hr-resume-demo.dev.hyperplane.dev"
      }
    }
  }
}
```

After saving, restart your Kaji session. The tools will be available directly.
