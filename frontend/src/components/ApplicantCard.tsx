import { MapPin, CheckSquare, Mail, Calendar, MessageSquare, GripVertical } from 'lucide-react'
import type { Applicant } from '../types'
import ScoreBar from './ScoreBar'

interface Props {
  applicant: Applicant
  selected: boolean
  onSelect: (id: string) => void
  onClick: (a: Applicant) => void
  scoring: boolean
  onDragStart: (id: string) => void
}

const STATUS_COLORS: Record<string, string> = {
  new: 'bg-gray-100 text-gray-600',
  reviewing: 'bg-blue-100 text-blue-700',
  shortlisted: 'bg-emerald-100 text-emerald-700',
  awaiting_reply: 'bg-amber-100 text-amber-700',
  booked: 'bg-purple-100 text-purple-700',
  rejected: 'bg-red-100 text-red-600',
  hired: 'bg-green-100 text-green-700',
}

export default function ApplicantCard({ applicant, selected, onSelect, onClick, scoring, onDragStart }: Props) {
  const sd = applicant.score_data
  const rd = applicant.response_data
  const certCount = applicant.resume.certifications.length
  const skiYears = applicant.resume.experience.filter(e => e.ski_related).reduce((s, e) => s + e.years, 0)

  return (
    <div
      draggable
      onDragStart={e => { e.dataTransfer.effectAllowed = 'move'; onDragStart(applicant.id) }}
      onClick={() => onClick(applicant)}
      className={`bg-white rounded-lg p-3 shadow-sm border-2 cursor-pointer transition-all hover:shadow-md select-none ${
        selected ? 'border-blue-500' : 'border-transparent'
      } ${scoring && !sd ? 'opacity-60' : ''}`}
    >
      <div className="flex items-start gap-2">
        <div className="flex flex-col gap-1 items-center pt-0.5">
          <input
            type="checkbox"
            checked={selected}
            onChange={() => onSelect(applicant.id)}
            onClick={e => e.stopPropagation()}
            className="cursor-pointer accent-blue-600"
          />
          <GripVertical size={12} className="text-gray-300 cursor-grab" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-1">
            <p className="font-semibold text-sm text-gray-900 truncate">
              {applicant.first_name} {applicant.last_name}
            </p>
            {sd && (
              <span className="text-xs font-bold text-gray-700 whitespace-nowrap">
                {sd.badge} {sd.score}
              </span>
            )}
          </div>

          {sd && <ScoreBar score={sd.score} max={sd.max_score} />}

          {rd && (
            <div className="mt-1 flex items-center gap-1">
              <ScoreBar score={rd.score} max={rd.max_score} animate={false} />
              <span className="text-xs text-indigo-600 font-medium whitespace-nowrap">💬 {rd.score}/50</span>
            </div>
          )}

          <div className="flex items-center gap-2 mt-1.5 text-xs text-gray-500 flex-wrap">
            <span className="flex items-center gap-0.5">
              <MapPin size={10} />
              {applicant.distance_miles.toFixed(0)}mi
            </span>
            {skiYears > 0 && <span className="text-blue-600 font-medium">{skiYears}yr ski</span>}
            {certCount > 0 && (
              <span className="flex items-center gap-0.5 text-emerald-600">
                <CheckSquare size={10} />
                {certCount}
              </span>
            )}
            {applicant.email_sent_at && !rd && (
              <span className="flex items-center gap-0.5 text-amber-600">
                <Mail size={10} />
                sent
              </span>
            )}
            {rd && (
              <span className="flex items-center gap-0.5 text-indigo-600 font-medium">
                <MessageSquare size={10} />
                replied
              </span>
            )}
            {applicant.calendar_event && (
              <span className="flex items-center gap-0.5 text-purple-600">
                <Calendar size={10} />
                {applicant.calendar_event.time}
              </span>
            )}
          </div>

          <div className="flex items-center justify-between mt-1.5">
            <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${STATUS_COLORS[applicant.status] ?? 'bg-gray-100 text-gray-600'}`}>
              {applicant.status.replace('_', ' ')}
            </span>
            {sd && !rd && (
              <span className={`text-xs font-medium ${
                sd.recommendation === 'Strong Hire' ? 'text-emerald-600' :
                sd.recommendation === 'Consider' ? 'text-yellow-600' : 'text-red-500'
              }`}>
                {sd.recommendation}
              </span>
            )}
            {rd && (
              <span className={`text-xs font-medium ${
                rd.recommendation === 'Strong' ? 'text-emerald-600' :
                rd.recommendation === 'Adequate' ? 'text-yellow-600' : 'text-red-500'
              }`}>
                {rd.recommendation} reply
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
