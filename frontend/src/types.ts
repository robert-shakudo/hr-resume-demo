export type ApplicantStatus = 'new' | 'reviewing' | 'shortlisted' | 'rejected' | 'hired'

export interface Experience {
  title: string
  company: string
  years: number
  ski_related: boolean
}

export interface Resume {
  summary: string
  experience: Experience[]
  certifications: string[]
  availability: { weekends: boolean; holidays: boolean; early_am: boolean }
  skills: string[]
}

export interface ScoreBreakdown {
  points: number
  max: number
}

export interface ScoreData {
  score: number
  max_score: number
  recommendation: string
  badge: string
  breakdown: Record<string, ScoreBreakdown>
  reasons: string[]
}

export interface Applicant {
  id: string
  first_name: string
  last_name: string
  email: string
  phone: string
  location: string
  distance_miles: number
  applied_date: string
  status: ApplicantStatus
  resume: Resume
  score_data?: ScoreData
}

export interface JobPosting {
  id: string
  title: string
  department: string
  location: string
  type: string
  season: string
  applicant_count: number
  loaded_count: number
  description: string
  requirements: string[]
  scoring_criteria: Record<string, number>
}
