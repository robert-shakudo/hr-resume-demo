import { useState } from 'react'
import { X, ChevronLeft, ChevronRight, Send, Mail, HelpCircle, TestTube } from 'lucide-react'
import type { EmailPreview } from '../api'

interface Props {
  previews: EmailPreview[]
  onSend: () => void
  onClose: () => void
}

export default function EmailPreviewModal({ previews, onSend, onClose }: Props) {
  const [idx, setIdx] = useState(0)
  const current = previews[idx]
  const isMock = current.mode === 'mock'

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl flex flex-col max-h-[88vh]">
        <div className="flex items-center justify-between p-5 border-b">
          <div className="flex items-center gap-2">
            <Mail size={18} className="text-blue-600" />
            <h2 className="font-bold text-gray-900">Email Preview</h2>
            <span className="text-sm text-gray-500">({previews.length} recipient{previews.length > 1 ? 's' : ''})</span>
            {isMock ? (
              <span className="flex items-center gap-1 text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-medium">
                <TestTube size={10} /> Mock Mode
              </span>
            ) : (
              <span className="flex items-center gap-1 text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-medium">
                <Send size={10} /> Live Send
              </span>
            )}
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-gray-100 rounded-lg">
            <X size={18} />
          </button>
        </div>

        {previews.length > 1 && (
          <div className="flex items-center justify-between px-5 py-2 border-b bg-gray-50 text-sm">
            <button onClick={() => setIdx(i => Math.max(0, i - 1))} disabled={idx === 0} className="p-1 hover:bg-gray-200 rounded disabled:opacity-40">
              <ChevronLeft size={16} />
            </button>
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-gray-500">{current.name}</span>
              <div className="flex gap-1">
                {previews.map((_, i) => (
                  <button key={i} onClick={() => setIdx(i)} className={`w-2 h-2 rounded-full transition-colors ${i === idx ? 'bg-blue-600' : 'bg-gray-300'}`} />
                ))}
              </div>
            </div>
            <button onClick={() => setIdx(i => Math.min(previews.length - 1, i + 1))} disabled={idx === previews.length - 1} className="p-1 hover:bg-gray-200 rounded disabled:opacity-40">
              <ChevronRight size={16} />
            </button>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-5 space-y-3">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-0.5">To (candidate)</p>
              <p className="font-medium text-gray-900">{current.name}</p>
              <p className="text-gray-500 text-xs">{current.actual_email}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              {isMock ? (
                <>
                  <p className="text-xs text-amber-600 mb-0.5 font-medium">⚗️ Sending to (mock)</p>
                  <p className="text-gray-700 text-xs">{current.email}</p>
                  <p className="text-xs text-gray-400 mt-0.5">Change in Settings → Email → Mock Email</p>
                </>
              ) : (
                <>
                  <p className="text-xs text-emerald-600 mb-0.5 font-medium">📤 Sending to (real)</p>
                  <p className="text-gray-700 text-xs">{current.email}</p>
                </>
              )}
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg px-3 py-2">
            <p className="text-xs text-gray-500 mb-0.5">Subject</p>
            <p className="font-medium text-gray-900 text-sm">{current.subject}</p>
          </div>

          {current.questions && current.questions.length > 0 && (
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-3">
              <p className="text-xs font-semibold text-blue-700 flex items-center gap-1 mb-1.5">
                <HelpCircle size={12} />
                Personalized questions for {current.name.split(' ')[0]}
              </p>
              {current.questions.map((q, i) => (
                <p key={i} className="text-xs text-blue-800">
                  {i + 1}. {q}
                </p>
              ))}
            </div>
          )}

          <div className="border border-gray-200 rounded-xl p-4">
            <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">
              {current.body}
            </pre>
          </div>
        </div>

        <div className="flex justify-between items-center p-4 border-t bg-gray-50 rounded-b-2xl">
          <p className="text-xs text-gray-500">
            {isMock
              ? `Mock: emails logged, not delivered. ${previews.length} candidate${previews.length > 1 ? 's' : ''} → Awaiting Reply`
              : `Live: sending to ${previews.length} real email address${previews.length > 1 ? 'es' : ''}`
            }
          </p>
          <div className="flex gap-2">
            <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">Cancel</button>
            <button onClick={onSend} className="flex items-center gap-2 bg-emerald-600 text-white px-5 py-2 rounded-lg hover:bg-emerald-700 transition-colors font-medium text-sm">
              <Send size={14} />
              {isMock ? `Send (Mock) ${previews.length}` : `Send ${previews.length} Email${previews.length > 1 ? 's' : ''}`}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
