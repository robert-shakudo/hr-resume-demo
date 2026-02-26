# AI-Powered HR Resume Processing — Ski Lift Operator

Demo for Mountain Capital Partners showing end-to-end automated resume processing.

## What it does

- **Mock Paycom API** — 30 Ski Lift Operator applicants with realistic profiles
- **AI Scoring** — Scores each candidate against 5 criteria (ski experience, certifications, availability, proximity, physical background)
- **Kanban Pipeline** — Drag candidates through New → Reviewing → Shortlisted → Rejected → Hired
- **Bulk Actions** — Send interview invites, book Google Calendar slots, reject in bulk
- **AI Reply** — Simulate candidate follow-up emails with AI-drafted responses

## Stack

- **Backend**: Python FastAPI (mock Paycom + scoring engine)
- **Frontend**: React + Vite + Tailwind CSS
- **Deploy**: Shakudo microservice on port 8787

## Run locally

```bash
cd backend && pip install -r requirements.txt
cd ../frontend && npm install && npm run build && cd ..
cd backend && uvicorn main:app --port 8787
```

Open http://localhost:8787

## Demo flow (~10 min)

1. Dashboard opens → 30 Ski Lift Operator applicants in "New" column
2. Click **Run AI Scoring** → watch candidates score in real-time
3. Select Top 10 (score ≥ 75) → **Send Invites** bulk action
4. Click any candidate → side panel shows full resume + score breakdown
5. Type a candidate reply → **AI Reply** drafts the response
