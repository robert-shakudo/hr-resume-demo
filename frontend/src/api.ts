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

export async function scoreAll(): Promise<{ scored: number; auto_promoted: number; threshold: number; results: any[] }> {
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

export async function previewEmails(ids: string[]): Promise<{ previews: EmailPreview[] }> {
  const r = await fetch(`${BASE}/email/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ applicant_ids: ids }),
  })
  return r.json()
}

export interface EmailPreview {
  id: string
  name: string
  email: string
  subject: string
  body: string
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

export async function fetchSettings(): Promise<any> {
  const r = await fetch(`${BASE}/settings`)
  return r.json()
}

export async function saveSettings(settings: any): Promise<any> {
  const r = await fetch(`${BASE}/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  })
  return r.json()
}

export async function paycomRefresh(): Promise<{ refreshed: boolean; applicant_count: number }> {
  const r = await fetch(`${BASE}/paycom/refresh`, { method: 'POST' })
  return r.json()
}

export async function uploadResume(data: {
  first_name: string
  last_name: string
  email: string
  location: string
  distance_miles: number
  resume_text: string
}): Promise<any> {
  const r = await fetch(`${BASE}/upload-resume`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  return r.json()
}
