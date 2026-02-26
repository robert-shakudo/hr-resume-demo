import { useState } from 'react'
import { X, Upload, UserPlus } from 'lucide-react'
import { uploadResume } from '../api'
import ScoreBar from './ScoreBar'

interface Props {
  onClose: () => void
  onUploaded: () => void
}

export default function UploadResumeModal({ onClose, onUploaded }: Props) {
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    location: '',
    distance_miles: '',
    resume_text: '',
  })
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const set = (k: string, v: string) => setForm(prev => ({ ...prev, [k]: v }))

  const handleSubmit = async () => {
    if (!form.first_name || !form.last_name || !form.email || !form.resume_text) {
      setError('Name, email, and resume text are required.')
      return
    }
    setError('')
    setLoading(true)
    try {
      const res = await uploadResume({
        ...form,
        distance_miles: parseFloat(form.distance_miles) || 50,
      })
      setResult(res)
    } catch {
      setError('Upload failed. Please try again.')
    }
    setLoading(false)
  }

  if (result) {
    const sd = result.score_data
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
          <div className="text-center mb-4">
            <div className="text-4xl mb-2">✅</div>
            <h3 className="font-bold text-gray-900 text-lg">Resume Added & Scored</h3>
            <p className="text-sm text-gray-500">{result.applicant.first_name} {result.applicant.last_name}</p>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold text-gray-800">AI Score</span>
              <span className="text-2xl font-black text-gray-900">
                {sd.badge} {sd.score}/100
              </span>
            </div>
            <ScoreBar score={sd.score} max={sd.max_score} />
            <p className={`text-sm font-medium mt-2 ${
              sd.recommendation === 'Strong Hire' ? 'text-emerald-600' :
              sd.recommendation === 'Consider' ? 'text-yellow-600' :
              sd.recommendation === 'Weak Candidate' ? 'text-orange-500' : 'text-red-500'
            }`}>
              {sd.recommendation}
            </p>
            <div className="mt-3 space-y-1">
              {sd.reasons.map((r: string, i: number) => (
                <p key={i} className="text-xs text-gray-700">{r}</p>
              ))}
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => { onUploaded(); onClose() }}
              className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
            >
              View in Dashboard
            </button>
            <button
              onClick={() => { setResult(null); setForm({ first_name: '', last_name: '', email: '', location: '', distance_miles: '', resume_text: '' }) }}
              className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700"
            >
              Add Another
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between p-5 border-b">
          <div className="flex items-center gap-2">
            <UserPlus size={18} className="text-blue-600" />
            <h2 className="font-bold text-gray-900">Upload Resume</h2>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-gray-100 rounded-lg">
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          <div className="grid grid-cols-2 gap-3">
            {[
              { k: 'first_name', label: 'First Name', ph: 'Jake' },
              { k: 'last_name', label: 'Last Name', ph: 'Morrison' },
            ].map(({ k, label, ph }) => (
              <div key={k}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                <input
                  value={form[k as keyof typeof form]}
                  onChange={e => set(k, e.target.value)}
                  placeholder={ph}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>
            ))}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              value={form.email}
              onChange={e => set('email', e.target.value)}
              placeholder="jake@email.com"
              type="email"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <input
                value={form.location}
                onChange={e => set('location', e.target.value)}
                placeholder="Vail, CO"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Miles from Resort</label>
              <input
                value={form.distance_miles}
                onChange={e => set('distance_miles', e.target.value)}
                placeholder="5.0"
                type="number"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Resume Text</label>
            <p className="text-xs text-gray-400 mb-1.5">
              Paste the resume or a summary. The AI will extract experience, certifications, and availability.
            </p>
            <textarea
              value={form.resume_text}
              onChange={e => set('resume_text', e.target.value)}
              rows={10}
              placeholder="3 seasons at Breckenridge as lift operator. OSHA 10 certified. First Aid/CPR. Available weekends, holidays, and 6am shifts. Strong physical endurance from outdoor work..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none"
            />
          </div>

          {error && (
            <p className="text-sm text-red-500">{error}</p>
          )}
        </div>

        <div className="flex justify-end gap-2 p-4 border-t bg-gray-50 rounded-b-2xl">
          <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">Cancel</button>
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm disabled:opacity-60"
          >
            <Upload size={14} />
            {loading ? 'Scoring...' : 'Upload & Score'}
          </button>
        </div>
      </div>
    </div>
  )
}
