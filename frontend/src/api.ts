import type { Applicant, JobPosting } from './types'

const BASE = '/api'

export async function fetchJob(): Promise<JobPosting> {
  const r = await fetch(`${BASE}/job`)
  return r.json()
}

export async function fetchApplicants(): Promise<Applicant[]> {
  const r = await fetch(`${BASE}/applicants`)
  return r.json()
}

export async function scoreAll(): Promise<{ scored: number; results: any[] }> {
  const r = await fetch(`${BASE}/score/all`, { method: 'POST' })
  return r.json()
}

export async function updateStatus(id: string, status: string): Promise<void> {
  await fetch(`${BASE}/applicants/${id}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  })
}

export async function bulkAction(ids: string[], action: string): Promise<any> {
  const r = await fetch(`${BASE}/bulk`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ applicant_ids: ids, action }),
  })
  return r.json()
}

export async function simulateReply(applicant_id: string, message: string): Promise<any> {
  const r = await fetch(`${BASE}/simulate-reply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ applicant_id, message }),
  })
  return r.json()
}
