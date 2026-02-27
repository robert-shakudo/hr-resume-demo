import { X, Mail, Phone, MapPin, Calendar, Award, Briefcase, Clock, MessageSquare } from 'lucide-react'
import type { Applicant } from '../types'
import ScoreBar from './ScoreBar'

interface Props {
  applicant: Applicant
  onClose: () => void
  onStatusChange: (id: string, status: string) => void
  onSendInvite: (id: string) => void
}

export default function ResumePanel({ applicant, onClose, onStatusChange, onSendInvite }: Props) {
  const sd = applicant.score_data
  const rd = applicant.response_data
  const ce = applicant.calendar_event
  const skiJobs = applicant.resume.experience.filter(e => e.ski_related)
  const otherJobs = applicant.resume.experience.filter(e => !e.ski_related)

  return (
    <div className="h-full flex flex-col bg-white border-l border-gray-200 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b bg-gray-50">
        <div>
          <h2 className="font-bold text-gray-900 text-lg">
            {applicant.first_name} {applicant.last_name}
          </h2>
          <p className="text-xs text-gray-500">{applicant.id}</p>
        </div>
        <button onClick={onClose} className="p-1.5 hover:bg-gray-200 rounded-lg transition-colors">
          <X size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="grid grid-cols-2 gap-2 text-sm">
          <span className="flex items-center gap-1.5 text-gray-600">
            <Mail size={13} className="text-blue-500" />
            <a href={`mailto:${applicant.email}`} className="text-blue-600 hover:underline truncate text-xs">{applicant.email}</a>
          </span>
          <span className="flex items-center gap-1.5 text-gray-600 text-xs">
            <Phone size={13} className="text-blue-500" />
            {applicant.phone}
          </span>
          <span className="flex items-center gap-1.5 text-gray-600 text-xs">
            <MapPin size={13} className="text-blue-500" />
            {applicant.location} ({applicant.distance_miles.toFixed(1)} mi)
          </span>
          <span className="flex items-center gap-1.5 text-gray-600 text-xs">
            <Calendar size={13} className="text-blue-500" />
            Applied {applicant.applied_date}
          </span>
        </div>

        {ce && (
          <div className="bg-purple-50 border border-purple-200 rounded-xl p-3">
            <div className="flex items-center gap-2 mb-1">
              <Calendar size={14} className="text-purple-600" />
              <span className="font-semibold text-sm text-purple-900">Interview Booked</span>
            </div>
            <p className="text-xs text-purple-800 font-medium">{ce.title}</p>
            <p className="text-xs text-purple-700 mt-0.5">{ce.date} at {ce.time} · {ce.duration}</p>
            <p className="text-xs text-purple-600">{ce.location}</p>
          </div>
        )}

        {sd ? (
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-gray-800 text-sm">Resume Score</h3>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-black text-gray-900">{sd.score}</span>
                <span className="text-gray-400 text-xs">/100</span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                  sd.recommendation === 'Strong Hire' ? 'bg-emerald-100 text-emerald-700' :
                  sd.recommendation === 'Consider' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {sd.badge} {sd.recommendation}
                </span>
              </div>
            </div>
            <div className="space-y-1.5">
              {Object.entries(sd.breakdown).map(([key, val]) => (
                <div key={key}>
                  <div className="flex justify-between text-xs text-gray-600 mb-0.5">
                    <span>{key}</span>
                    <span className="font-medium">{val.points}/{val.max}</span>
                  </div>
                  <ScoreBar score={val.points} max={val.max} />
                </div>
              ))}
            </div>
            <div className="mt-2 space-y-0.5">
              {sd.reasons.map((r, i) => <p key={i} className="text-xs text-gray-700">{r}</p>)}
            </div>
          </div>
        ) : (
          <div className="bg-gray-50 rounded-xl p-4 border border-dashed border-gray-200 text-center text-sm text-gray-400">
            Run AI scoring to see candidate analysis
          </div>
        )}

        {rd && (
          <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-4 border border-indigo-100">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-bold text-gray-800 text-sm flex items-center gap-1.5">
                <MessageSquare size={13} className="text-indigo-600" />
                Candidate Response Score
              </h3>
              <div className="flex items-center gap-1.5">
                <span className="text-xl font-black text-gray-900">{rd.score}</span>
                <span className="text-gray-400 text-xs">/50</span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                  rd.recommendation === 'Strong' ? 'bg-emerald-100 text-emerald-700' :
                  rd.recommendation === 'Adequate' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {rd.recommendation}
                </span>
              </div>
            </div>
            <div className="bg-white rounded-lg p-2.5 mb-2 text-xs text-gray-700 leading-relaxed border">
              "{rd.text}"
            </div>
            <div className="space-y-1">
              {Object.entries(rd.breakdown).map(([key, val]) => (
                <div key={key}>
                  <div className="flex justify-between text-xs text-gray-600 mb-0.5">
                    <span>{key}</span><span className="font-medium">{val.points}/{val.max}</span>
                  </div>
                  <ScoreBar score={val.points} max={val.max} animate={false} />
                </div>
              ))}
            </div>
            <div className="mt-1.5 space-y-0.5">
              {rd.reasons.map((r, i) => <p key={i} className="text-xs text-gray-700">{r}</p>)}
            </div>
            {sd && (
              <div className="mt-2 pt-2 border-t border-indigo-100">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600 font-medium">Combined Score</span>
                  <span className="font-black text-gray-900 text-base">
                    {Math.round((sd.score + rd.score * 0.5))} / 125
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-0.5">Resume (100) + Response (50) weighted</p>
              </div>
            )}
          </div>
        )}

        <div>
          <h3 className="font-semibold text-gray-800 text-sm mb-1.5">Summary</h3>
          <p className="text-sm text-gray-700 leading-relaxed bg-gray-50 p-3 rounded-lg">
            {applicant.resume.summary}
          </p>
        </div>

        <div>
          <h3 className="font-semibold text-gray-800 text-sm mb-1.5 flex items-center gap-1.5">
            <Briefcase size={13} />
            Experience
          </h3>
          <div className="space-y-1.5">
            {skiJobs.map((e, i) => (
              <div key={i} className="flex items-start gap-2 p-2 bg-blue-50 rounded-lg border border-blue-100">
                <span className="text-base">⛷️</span>
                <div>
                  <p className="font-medium text-xs text-gray-900">{e.title}</p>
                  <p className="text-xs text-gray-600">{e.company} · {e.years}yr</p>
                </div>
              </div>
            ))}
            {otherJobs.map((e, i) => (
              <div key={i} className="flex items-start gap-2 p-2 bg-gray-50 rounded-lg">
                <span className="text-base">💼</span>
                <div>
                  <p className="font-medium text-xs text-gray-900">{e.title}</p>
                  <p className="text-xs text-gray-600">{e.company} · {e.years}yr</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-semibold text-gray-800 text-sm mb-1.5 flex items-center gap-1.5">
            <Award size={13} />
            Certifications
          </h3>
          {applicant.resume.certifications.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {applicant.resume.certifications.map((c, i) => (
                <span key={i} className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full font-medium">{c}</span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-gray-400 italic">No certifications listed</p>
          )}
        </div>

        <div>
          <h3 className="font-semibold text-gray-800 text-sm mb-1.5 flex items-center gap-1.5">
            <Clock size={13} />
            Availability
          </h3>
          <div className="flex gap-2">
            {[{ key: 'weekends', label: 'Weekends' }, { key: 'holidays', label: 'Holidays' }, { key: 'early_am', label: 'Early AM' }].map(({ key, label }) => (
              <span key={key} className={`text-xs px-2 py-1 rounded-full font-medium ${
                applicant.resume.availability[key as keyof typeof applicant.resume.availability]
                  ? 'bg-emerald-100 text-emerald-700' : 'bg-red-50 text-red-500'
              }`}>
                {applicant.resume.availability[key as keyof typeof applicant.resume.availability] ? '✓' : '✗'} {label}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="p-3 border-t bg-gray-50 space-y-2">
        <div className="flex gap-2">
          <select
            value={applicant.status}
            onChange={e => onStatusChange(applicant.id, e.target.value)}
            className="flex-1 text-sm border border-gray-300 rounded-lg px-2 py-1.5 bg-white focus:ring-2 focus:ring-blue-500 outline-none"
          >
            {['new','reviewing','shortlisted','awaiting_reply','booked','rejected','hired'].map(s => (
              <option key={s} value={s}>{s.replace('_', ' ')}</option>
            ))}
          </select>
          <button
            onClick={() => onSendInvite(applicant.id)}
            className="flex items-center gap-1.5 bg-blue-600 text-white text-sm px-3 py-1.5 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            <Mail size={13} />
            Send Invite
          </button>
        </div>
      </div>
    </div>
  )
}
