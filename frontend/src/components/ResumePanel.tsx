import { X, Mail, Phone, MapPin, Calendar, Award, Briefcase, Clock } from 'lucide-react'
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
  const skiJobs = applicant.resume.experience.filter(e => e.ski_related)
  const otherJobs = applicant.resume.experience.filter(e => !e.ski_related)

  return (
    <div className="h-full flex flex-col bg-white border-l border-gray-200 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b bg-gray-50">
        <div>
          <h2 className="font-bold text-gray-900 text-lg">
            {applicant.first_name} {applicant.last_name}
          </h2>
          <p className="text-sm text-gray-500">{applicant.id}</p>
        </div>
        <button onClick={onClose} className="p-1.5 hover:bg-gray-200 rounded-lg transition-colors">
          <X size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="grid grid-cols-2 gap-2 text-sm">
          <span className="flex items-center gap-1.5 text-gray-600">
            <Mail size={13} className="text-blue-500" />
            <a href={`mailto:${applicant.email}`} className="text-blue-600 hover:underline truncate">
              {applicant.email}
            </a>
          </span>
          <span className="flex items-center gap-1.5 text-gray-600">
            <Phone size={13} className="text-blue-500" />
            {applicant.phone}
          </span>
          <span className="flex items-center gap-1.5 text-gray-600">
            <MapPin size={13} className="text-blue-500" />
            {applicant.location} ({applicant.distance_miles.toFixed(1)} mi)
          </span>
          <span className="flex items-center gap-1.5 text-gray-600">
            <Calendar size={13} className="text-blue-500" />
            Applied {applicant.applied_date}
          </span>
        </div>

        {sd ? (
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-gray-800">AI Score</h3>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-black text-gray-900">{sd.score}</span>
                <span className="text-gray-400 text-sm">/100</span>
                <span className={`text-sm font-bold px-2 py-0.5 rounded-full ${
                  sd.recommendation === 'Strong Hire' ? 'bg-emerald-100 text-emerald-700' :
                  sd.recommendation === 'Consider' ? 'bg-yellow-100 text-yellow-700' :
                  sd.recommendation === 'Weak Candidate' ? 'bg-orange-100 text-orange-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {sd.badge} {sd.recommendation}
                </span>
              </div>
            </div>

            <div className="space-y-2">
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

            <div className="mt-3 space-y-1">
              {sd.reasons.map((r, i) => (
                <p key={i} className="text-xs text-gray-700">{r}</p>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-gray-50 rounded-xl p-4 border border-dashed border-gray-200 text-center text-sm text-gray-400">
            Run AI scoring to see candidate analysis
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
          <div className="space-y-2">
            {skiJobs.map((e, i) => (
              <div key={i} className="flex items-start gap-2 p-2.5 bg-blue-50 rounded-lg border border-blue-100">
                <span className="text-blue-500 text-lg">⛷️</span>
                <div>
                  <p className="font-medium text-sm text-gray-900">{e.title}</p>
                  <p className="text-xs text-gray-600">{e.company} · {e.years} yr{e.years > 1 ? 's' : ''}</p>
                </div>
              </div>
            ))}
            {otherJobs.map((e, i) => (
              <div key={i} className="flex items-start gap-2 p-2.5 bg-gray-50 rounded-lg">
                <span className="text-gray-400 text-lg">💼</span>
                <div>
                  <p className="font-medium text-sm text-gray-900">{e.title}</p>
                  <p className="text-xs text-gray-600">{e.company} · {e.years} yr{e.years > 1 ? 's' : ''}</p>
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
                <span key={i} className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full font-medium">
                  {c}
                </span>
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
            {[
              { key: 'weekends', label: 'Weekends' },
              { key: 'holidays', label: 'Holidays' },
              { key: 'early_am', label: 'Early AM' },
            ].map(({ key, label }) => (
              <span key={key} className={`text-xs px-2 py-1 rounded-full font-medium ${
                applicant.resume.availability[key as keyof typeof applicant.resume.availability]
                  ? 'bg-emerald-100 text-emerald-700'
                  : 'bg-red-50 text-red-500'
              }`}>
                {applicant.resume.availability[key as keyof typeof applicant.resume.availability] ? '✓' : '✗'} {label}
              </span>
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-semibold text-gray-800 text-sm mb-1.5">Skills</h3>
          <div className="flex flex-wrap gap-1.5">
            {applicant.resume.skills.map((s, i) => (
              <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                {s}
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
            <option value="new">New</option>
            <option value="reviewing">Reviewing</option>
            <option value="shortlisted">Shortlisted</option>
            <option value="rejected">Rejected</option>
            <option value="hired">Hired</option>
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
