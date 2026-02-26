import { useState, useEffect } from 'react'
import { X, Save, RotateCcw, Sliders, Mail, HelpCircle, Plus, Trash2 } from 'lucide-react'
import { fetchSettings, saveSettings } from '../api'

interface Props {
  onClose: () => void
  onSaved: () => void
}

type Tab = 'scoring' | 'email' | 'questions'

export default function SettingsModal({ onClose, onSaved }: Props) {
  const [tab, setTab] = useState<Tab>('scoring')
  const [settings, setSettings] = useState<any>(null)
  const [saving, setSaving] = useState(false)
  const [emailPreviewText, setEmailPreviewText] = useState('')

  useEffect(() => {
    fetchSettings().then(s => {
      setSettings(s)
      renderPreview(s)
    })
  }, [])

  const renderPreview = (s: any) => {
    if (!s) return
    let preview = s.email.template
    preview = preview.replace('{{first_name}}', 'Jake')
    preview = preview.replace('{{last_name}}', 'Morrison')
    preview = preview.replace('{{ski_experience_note}}', ' — particularly your 3 years of ski resort experience')
    preview = preview.replace('{{interview_details}}', s.email.interview_details)
    preview = preview.replace('{{location}}', 'Breckenridge, CO')
    preview = preview.replace('{{score}}', '87')
    setEmailPreviewText(preview)
  }

  const handleSave = async () => {
    setSaving(true)
    await saveSettings(settings)
    setSaving(false)
    onSaved()
    onClose()
  }

  const updateScoring = (key: string, val: number) => {
    setSettings((prev: any) => ({
      ...prev,
      scoring: { ...prev.scoring, [key]: val },
    }))
  }

  const updateEmailField = (key: string, val: string) => {
    const next = { ...settings, email: { ...settings.email, [key]: val } }
    setSettings(next)
    if (key === 'template' || key === 'interview_details') {
      renderPreview(next)
    }
  }

  const updateQuestion = (i: number, val: string) => {
    const qs = [...settings.questions]
    qs[i] = val
    setSettings((prev: any) => ({ ...prev, questions: qs }))
  }

  const addQuestion = () => {
    setSettings((prev: any) => ({ ...prev, questions: [...prev.questions, ''] }))
  }

  const removeQuestion = (i: number) => {
    const qs = settings.questions.filter((_: string, idx: number) => idx !== i)
    setSettings((prev: any) => ({ ...prev, questions: qs }))
  }

  if (!settings) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8 text-gray-500">Loading settings...</div>
      </div>
    )
  }

  const TABS: { key: Tab; label: string; icon: typeof Sliders }[] = [
    { key: 'scoring', label: 'AI Scoring', icon: Sliders },
    { key: 'email', label: 'Email', icon: Mail },
    { key: 'questions', label: 'Questions', icon: HelpCircle },
  ]

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between p-5 border-b">
          <h2 className="font-bold text-gray-900 text-xl">Settings</h2>
          <button onClick={onClose} className="p-1.5 hover:bg-gray-100 rounded-lg">
            <X size={18} />
          </button>
        </div>

        <div className="flex border-b px-5">
          {TABS.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                tab === key
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon size={14} />
              {label}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto p-5">
          {tab === 'scoring' && (
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-gray-800 mb-4">Auto-Promote Thresholds</h3>
                <p className="text-sm text-gray-500 mb-4">
                  After scoring, candidates at or above the auto-promote threshold are automatically moved to <strong>Reviewing</strong>.
                </p>
                <div className="space-y-4">
                  {[
                    { key: 'auto_promote_threshold', label: 'Auto-Promote Threshold', desc: 'Moves "New" → "Reviewing" automatically', color: 'text-blue-600' },
                    { key: 'strong_hire_threshold', label: 'Strong Hire Threshold', desc: 'Shown as 🟢 Strong Hire badge', color: 'text-emerald-600' },
                    { key: 'consider_threshold', label: 'Consider Threshold', desc: 'Shown as 🟡 Consider badge', color: 'text-yellow-600' },
                  ].map(({ key, label, desc, color }) => (
                    <div key={key} className="bg-gray-50 rounded-xl p-4">
                      <div className="flex items-center justify-between mb-1">
                        <label className="font-medium text-sm text-gray-800">{label}</label>
                        <span className={`font-bold text-lg ${color}`}>
                          {settings.scoring[key]}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 mb-2">{desc}</p>
                      <input
                        type="range"
                        min={0}
                        max={100}
                        value={settings.scoring[key]}
                        onChange={e => updateScoring(key, Number(e.target.value))}
                        className="w-full accent-blue-600"
                      />
                      <div className="flex justify-between text-xs text-gray-400 mt-0.5">
                        <span>0</span>
                        <span>50</span>
                        <span>100</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-blue-50 rounded-xl p-4 text-sm text-blue-800">
                <strong>Scoring weights</strong> are fixed in this demo (Ski Experience 35pts · Certs 25pts · Availability 20pts · Proximity 15pts · Physical 5pts). Thresholds above control how candidates are bucketed.
              </div>
            </div>
          )}

          {tab === 'email' && (
            <div className="grid grid-cols-2 gap-5">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Subject Line</label>
                  <input
                    value={settings.email.subject}
                    onChange={e => updateEmailField('subject', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email Body Template</label>
                  <p className="text-xs text-gray-400 mb-1.5">
                    Variables: <code className="bg-gray-100 px-1 rounded">{'{{first_name}}'}</code> <code className="bg-gray-100 px-1 rounded">{'{{ski_experience_note}}'}</code> <code className="bg-gray-100 px-1 rounded">{'{{interview_details}}'}</code>
                  </p>
                  <textarea
                    value={settings.email.template}
                    onChange={e => updateEmailField('template', e.target.value)}
                    rows={12}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:ring-2 focus:ring-blue-500 outline-none resize-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Interview Details Snippet</label>
                  <textarea
                    value={settings.email.interview_details}
                    onChange={e => updateEmailField('interview_details', e.target.value)}
                    rows={3}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Live Preview <span className="text-gray-400 font-normal">(Jake Morrison, 3yr ski exp, score 87)</span>
                </label>
                <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-sm text-gray-700 leading-relaxed whitespace-pre-wrap font-sans h-full min-h-64 overflow-y-auto">
                  <p className="font-medium text-gray-900 mb-2 text-xs uppercase tracking-wide text-gray-500">Subject: {settings.email.subject}</p>
                  <hr className="mb-3" />
                  {emailPreviewText}
                </div>
              </div>
            </div>
          )}

          {tab === 'questions' && (
            <div className="space-y-3">
              <p className="text-sm text-gray-500">
                These questions appear as a reference during interviews. They're shown in the candidate panel and can be included in invite emails.
              </p>
              {settings.questions.map((q: string, i: number) => (
                <div key={i} className="flex gap-2 items-start">
                  <span className="text-xs font-bold text-gray-400 mt-2.5 w-5 shrink-0">{i + 1}.</span>
                  <input
                    value={q}
                    onChange={e => updateQuestion(i, e.target.value)}
                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                  <button
                    onClick={() => removeQuestion(i)}
                    className="mt-1.5 p-1.5 text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
              <button
                onClick={addQuestion}
                className="flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 font-medium mt-2"
              >
                <Plus size={14} />
                Add question
              </button>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 p-4 border-t bg-gray-50 rounded-b-2xl">
          <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm disabled:opacity-60"
          >
            <Save size={14} />
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  )
}
