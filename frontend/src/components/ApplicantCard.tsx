import { MapPin, Calendar, CheckSquare } from 'lucide-react'
import type { Applicant } from '../types'
import ScoreBar from './ScoreBar'

interface Props {
  applicant: Applicant
  selected: boolean
  onSelect: (id: string) => void
  onClick: (a: Applicant) => void
  scoring: boolean
}

const STATUS_COLORS: Record<string, string> = {
  new: 'bg-gray-100 text-gray-600',
  reviewing: 'bg-blue-100 text-blue-700',
  shortlisted: 'bg-emerald-100 text-emerald-700',
  rejected: 'bg-red-100 text-red-600',
  hired: 'bg-purple-100 text-purple-700',
}

export default function ApplicantCard({ applicant, selected, onSelect, onClick, scoring }: Props) {
  const sd = applicant.score_data
  const certCount = applicant.resume.certifications.length
  const skiYears = applicant.resume.experience
    .filter(e => e.ski_related)
    .reduce((s, e) => s + e.years, 0)

  return (
    <div
      onClick={() => onClick(applicant)}
      className={`bg-white rounded-lg p-3 shadow-sm border-2 cursor-pointer transition-all hover:shadow-md ${
        selected ? 'border-blue-500' : 'border-transparent'
      } ${scoring && !sd ? 'scoring-live opacity-70' : ''}`}
    >
      <div className="flex items-start gap-2">
        <input
          type="checkbox"
          checked={selected}
          onChange={() => onSelect(applicant.id)}
          onClick={e => e.stopPropagation()}
          className="mt-1 cursor-pointer accent-blue-600"
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-1">
            <p className="font-semibold text-sm text-gray-900 truncate">
              {applicant.first_name} {applicant.last_name}
            </p>
            {sd && (
              <span className="text-xs font-bold text-gray-700 whitespace-nowrap">
                {sd.badge} {sd.score}/100
              </span>
            )}
          </div>

          {sd && <ScoreBar score={sd.score} max={sd.max_score} />}

          <div className="flex items-center gap-3 mt-1.5 text-xs text-gray-500">
            <span className="flex items-center gap-0.5">
              <MapPin size={10} />
              {applicant.distance_miles.toFixed(0)}mi
            </span>
            {skiYears > 0 && (
              <span className="text-blue-600 font-medium">{skiYears}yr ski</span>
            )}
            {certCount > 0 && (
              <span className="flex items-center gap-0.5 text-emerald-600">
                <CheckSquare size={10} />
                {certCount} cert{certCount > 1 ? 's' : ''}
              </span>
            )}
          </div>

          <div className="flex items-center justify-between mt-1.5">
            <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${STATUS_COLORS[applicant.status]}`}>
              {applicant.status}
            </span>
            {sd && (
              <span className={`text-xs font-medium ${
                sd.recommendation === 'Strong Hire' ? 'text-emerald-600' :
                sd.recommendation === 'Consider' ? 'text-yellow-600' :
                sd.recommendation === 'Weak Candidate' ? 'text-orange-500' : 'text-red-500'
              }`}>
                {sd.recommendation}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
