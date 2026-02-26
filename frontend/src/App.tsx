import { useState, useEffect, useCallback } from 'react'
import { Zap, Settings, UserPlus, RefreshCw, Mail, CalendarCheck, Filter } from 'lucide-react'
import type { Applicant, JobPosting, ApplicantStatus } from './types'
import { fetchJob, fetchApplicants, scoreAll, updateStatus, previewEmails, bulkAction, simulateReply, paycomRefresh } from './api'
import ApplicantCard from './components/ApplicantCard'
import ResumePanel from './components/ResumePanel'
import SettingsModal from './components/SettingsModal'
import EmailPreviewModal from './components/EmailPreviewModal'
import UploadResumeModal from './components/UploadResumeModal'
import type { EmailPreview } from './api'

const COLUMNS: { key: ApplicantStatus; label: string; color: string }[] = [
  { key: 'new', label: 'New', color: 'bg-gray-100' },
  { key: 'reviewing', label: 'Reviewing', color: 'bg-blue-50' },
  { key: 'shortlisted', label: 'Shortlisted', color: 'bg-emerald-50' },
  { key: 'rejected', label: 'Rejected', color: 'bg-red-50' },
  { key: 'hired', label: 'Hired', color: 'bg-purple-50' },
]

export default function App() {
  const [job, setJob] = useState<JobPosting | null>(null)
  const [applicants, setApplicants] = useState<Applicant[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [activeApplicant, setActiveApplicant] = useState<Applicant | null>(null)
  const [scoring, setScoring] = useState(false)
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState<string | null>(null)
  const [filterMin, setFilterMin] = useState(0)
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [replyModal, setReplyModal] = useState<{ applicant: Applicant; reply: string } | null>(null)
  const [replyInput, setReplyInput] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const [emailPreviews, setEmailPreviews] = useState<EmailPreview[] | null>(null)
  const [showUpload, setShowUpload] = useState(false)
  const [syncing, setSyncing] = useState(false)

  const showToast = (msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3500)
  }

  const load = useCallback(async () => {
    const [j, apps] = await Promise.all([fetchJob(), fetchApplicants()])
    setJob(j)
    setApplicants(apps)
    setLoading(false)
  }, [])

  useEffect(() => { load() }, [load])

  const handleScoreAll = async () => {
    setScoring(true)
    showToast('🤖 AI scoring in progress...')
    const result = await scoreAll()
    await load()
    setScoring(false)
    if (result.auto_promoted > 0) {
      showToast(`✅ Scored ${result.scored} candidates — ${result.auto_promoted} auto-promoted to Reviewing (score ≥ ${result.threshold})`)
    } else {
      showToast(`✅ All ${result.scored} candidates scored`)
    }
  }

  const handleStatusChange = async (id: string, status: string) => {
    await updateStatus(id, status)
    await load()
    if (activeApplicant?.id === id) {
      setActiveApplicant(prev => prev ? { ...prev, status: status as ApplicantStatus } : prev)
    }
  }

  const handlePreviewAndSend = async () => {
    if (selected.size === 0) { showToast('Select at least one applicant'); return }
    const res = await previewEmails(Array.from(selected))
    setEmailPreviews(res.previews)
  }

  const handleConfirmSend = async () => {
    const ids = (emailPreviews ?? []).map(p => p.id)
    await bulkAction(ids, 'send_invite')
    await load()
    showToast(`✅ ${ids.length} personalised invite${ids.length > 1 ? 's' : ''} sent`)
    setEmailPreviews(null)
    setSelected(new Set())
  }

  const handleBulkAction = async (action: string) => {
    if (selected.size === 0) { showToast('Select at least one applicant'); return }
    const res = await bulkAction(Array.from(selected), action)
    await load()
    const label = action === 'reject' ? 'rejected' : 'interviews booked'
    showToast(`✅ ${res.processed} ${label}`)
    setSelected(new Set())
  }

  const handleSendInvite = async (id: string) => {
    const res = await previewEmails([id])
    setEmailPreviews(res.previews)
  }

  const handleSimulateReply = async () => {
    if (!activeApplicant || !replyInput.trim()) return
    const res = await simulateReply(activeApplicant.id, replyInput)
    setReplyModal({ applicant: activeApplicant, reply: res.ai_drafted_reply })
    setReplyInput('')
  }

  const handlePaycomRefresh = async () => {
    setSyncing(true)
    const res = await paycomRefresh()
    await load()
    setSelected(new Set())
    setActiveApplicant(null)
    setSyncing(false)
    showToast(`🔄 Pulled ${res.applicant_count} applicants from Paycom. All scores reset.`)
  }

  const toggleSelect = (id: string) => {
    setSelected(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const filteredApplicants = applicants.filter(a => {
    if (filterStatus !== 'all' && a.status !== filterStatus) return false
    if (filterMin > 0 && (a.score_data?.score ?? 0) < filterMin) return false
    return true
  })

  const byStatus = (status: ApplicantStatus) => filteredApplicants.filter(a => a.status === status)
  const scoredCount = applicants.filter(a => a.score_data).length
  const shortlistedCount = applicants.filter(a => a.status === 'shortlisted').length

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="text-5xl mb-4">⛷️</div>
          <p className="text-gray-600 font-medium">Loading Paycom data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b shadow-sm px-6 py-3">
        <div className="max-w-screen-2xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">⛷️</span>
            <div>
              <h1 className="font-bold text-gray-900 text-lg leading-tight">{job?.title}</h1>
              <p className="text-xs text-gray-500">{job?.location} · {job?.season} · {job?.type}</p>
            </div>
          </div>

          <div className="flex items-center gap-5">
            <div className="flex items-center gap-4 text-center">
              <div>
                <p className="text-2xl font-black text-gray-900">{job?.applicant_count}</p>
                <p className="text-xs text-gray-500">Total</p>
              </div>
              <div>
                <p className="text-2xl font-black text-blue-600">{scoredCount}</p>
                <p className="text-xs text-gray-500">Scored</p>
              </div>
              <div>
                <p className="text-2xl font-black text-emerald-600">{shortlistedCount}</p>
                <p className="text-xs text-gray-500">Shortlisted</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowUpload(true)}
                className="flex items-center gap-1.5 border border-gray-300 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
              >
                <UserPlus size={14} />
                Upload Resume
              </button>
              <button
                onClick={handlePaycomRefresh}
                disabled={syncing}
                className="flex items-center gap-1.5 border border-gray-300 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium disabled:opacity-60"
              >
                <RefreshCw size={14} className={syncing ? 'animate-spin' : ''} />
                {syncing ? 'Syncing...' : 'Sync Paycom'}
              </button>
              <button
                onClick={handleScoreAll}
                disabled={scoring}
                className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-60 transition-colors font-semibold text-sm shadow-sm"
              >
                <Zap size={15} className={scoring ? 'animate-pulse' : ''} />
                {scoring ? 'Scoring...' : 'Run AI Scoring'}
              </button>
              <button
                onClick={() => setShowSettings(true)}
                className="p-2 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50 transition-colors"
                title="Settings"
              >
                <Settings size={16} />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-screen-2xl mx-auto w-full flex-1 flex flex-col px-6 py-4 gap-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-sm text-gray-600 bg-white border rounded-lg px-3 py-1.5">
              <Filter size={13} />
              <select
                value={filterStatus}
                onChange={e => setFilterStatus(e.target.value)}
                className="outline-none bg-transparent text-sm"
              >
                <option value="all">All Statuses</option>
                {COLUMNS.map(c => <option key={c.key} value={c.key}>{c.label}</option>)}
              </select>
            </div>
            {scoredCount > 0 && (
              <div className="flex items-center gap-1.5 text-sm text-gray-600 bg-white border rounded-lg px-3 py-1.5">
                <span>Min Score:</span>
                <select
                  value={filterMin}
                  onChange={e => setFilterMin(Number(e.target.value))}
                  className="outline-none bg-transparent text-sm"
                >
                  <option value={0}>Any</option>
                  <option value={55}>55+ (Consider)</option>
                  <option value={75}>75+ (Strong Hire)</option>
                </select>
              </div>
            )}
            <span className="text-xs text-gray-400">{filteredApplicants.length} shown of {applicants.length}</span>
          </div>

          {selected.size > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-blue-700 bg-blue-50 px-2 py-1 rounded">
                {selected.size} selected
              </span>
              <button
                onClick={handlePreviewAndSend}
                className="flex items-center gap-1.5 text-sm bg-emerald-600 text-white px-3 py-1.5 rounded-lg hover:bg-emerald-700 transition-colors font-medium"
              >
                <Mail size={13} />
                Preview &amp; Send Invites
              </button>
              <button
                onClick={() => handleBulkAction('book_interview')}
                className="flex items-center gap-1.5 text-sm bg-indigo-600 text-white px-3 py-1.5 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
              >
                <CalendarCheck size={13} />
                Book Interviews
              </button>
              <button
                onClick={() => handleBulkAction('reject')}
                className="flex items-center gap-1.5 text-sm bg-red-500 text-white px-3 py-1.5 rounded-lg hover:bg-red-600 transition-colors font-medium"
              >
                Reject
              </button>
              <button onClick={() => setSelected(new Set())} className="text-sm text-gray-500 hover:text-gray-700 px-2 py-1.5">Clear</button>
            </div>
          )}
        </div>

        <div className="flex gap-4 flex-1 min-h-0">
          <div className={`flex gap-3 flex-1 overflow-x-auto ${activeApplicant ? 'hidden lg:flex' : 'flex'}`}>
            {COLUMNS.map(col => {
              const cards = byStatus(col.key)
              return (
                <div key={col.key} className={`flex-shrink-0 w-52 rounded-xl ${col.color} p-2 flex flex-col`}>
                  <div className="flex items-center justify-between px-1 pb-2">
                    <h3 className="font-bold text-xs text-gray-700 uppercase tracking-wide">{col.label}</h3>
                    <span className="text-xs bg-white text-gray-600 rounded-full px-1.5 py-0.5 font-bold shadow-sm">{cards.length}</span>
                  </div>
                  <div className="space-y-2 overflow-y-auto flex-1">
                    {cards.length === 0
                      ? <p className="text-xs text-gray-400 text-center py-4 italic">Empty</p>
                      : cards.map(a => (
                        <ApplicantCard
                          key={a.id}
                          applicant={a}
                          selected={selected.has(a.id)}
                          onSelect={toggleSelect}
                          onClick={setActiveApplicant}
                          scoring={scoring}
                        />
                      ))
                    }
                  </div>
                </div>
              )
            })}
          </div>

          {activeApplicant && (
            <div className="flex-shrink-0 w-full lg:w-96 xl:w-[420px] rounded-xl overflow-hidden shadow-md border border-gray-200 flex flex-col bg-white">
              <ResumePanel
                applicant={applicants.find(a => a.id === activeApplicant.id) ?? activeApplicant}
                onClose={() => setActiveApplicant(null)}
                onStatusChange={handleStatusChange}
                onSendInvite={handleSendInvite}
              />
              <div className="p-3 border-t">
                <p className="text-xs text-gray-500 mb-1.5 font-medium">Simulate candidate reply</p>
                <div className="flex gap-2">
                  <input
                    value={replyInput}
                    onChange={e => setReplyInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSimulateReply()}
                    placeholder="e.g. I can confirm the interview..."
                    className="flex-1 text-xs border border-gray-300 rounded-lg px-2.5 py-1.5 focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                  <button
                    onClick={handleSimulateReply}
                    className="text-xs bg-gray-800 text-white px-3 py-1.5 rounded-lg hover:bg-gray-700 transition-colors font-medium"
                  >
                    AI Reply
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-sm px-5 py-2.5 rounded-full shadow-xl z-50">
          {toast}
        </div>
      )}

      {replyModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-5">
            <h3 className="font-bold text-gray-900 mb-1">AI-Drafted Reply</h3>
            <p className="text-xs text-gray-500 mb-3">To: {replyModal.applicant.email}</p>
            <pre className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg whitespace-pre-wrap leading-relaxed font-sans border">
              {replyModal.reply}
            </pre>
            <div className="flex gap-2 mt-4">
              <button
                onClick={() => { setReplyModal(null); showToast('✅ Reply sent!') }}
                className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
              >
                Send Reply
              </button>
              <button onClick={() => setReplyModal(null)} className="px-4 py-2 text-gray-600 hover:text-gray-800 text-sm">Discard</button>
            </div>
          </div>
        </div>
      )}

      {showSettings && (
        <SettingsModal
          onClose={() => setShowSettings(false)}
          onSaved={() => showToast('✅ Settings saved')}
        />
      )}

      {emailPreviews && (
        <EmailPreviewModal
          previews={emailPreviews}
          onSend={handleConfirmSend}
          onClose={() => setEmailPreviews(null)}
        />
      )}

      {showUpload && (
        <UploadResumeModal
          onClose={() => setShowUpload(false)}
          onUploaded={() => { load(); showToast('✅ Resume added and scored') }}
        />
      )}
    </div>
  )
}
