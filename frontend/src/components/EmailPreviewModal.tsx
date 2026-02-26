import { useState } from 'react'
import { X, ChevronLeft, ChevronRight, Send, Mail } from 'lucide-react'
import type { EmailPreview } from '../api'

interface Props {
  previews: EmailPreview[]
  onSend: () => void
  onClose: () => void
}

export default function EmailPreviewModal({ previews, onSend, onClose }: Props) {
  const [idx, setIdx] = useState(0)
  const current = previews[idx]

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl flex flex-col max-h-[85vh]">
        <div className="flex items-center justify-between p-5 border-b">
          <div className="flex items-center gap-2">
            <Mail size={18} className="text-blue-600" />
            <h2 className="font-bold text-gray-900">Email Preview</h2>
            <span className="text-sm text-gray-500 ml-1">
              ({previews.length} recipient{previews.length > 1 ? 's' : ''})
            </span>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-gray-100 rounded-lg">
            <X size={18} />
          </button>
        </div>

        {previews.length > 1 && (
          <div className="flex items-center justify-between px-5 py-2.5 border-b bg-gray-50 text-sm">
            <button
              onClick={() => setIdx(i => Math.max(0, i - 1))}
              disabled={idx === 0}
              className="p-1 hover:bg-gray-200 rounded disabled:opacity-40"
            >
              <ChevronLeft size={16} />
            </button>
            <div className="flex items-center gap-2">
              {previews.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setIdx(i)}
                  className={`w-2 h-2 rounded-full transition-colors ${i === idx ? 'bg-blue-600' : 'bg-gray-300'}`}
                />
              ))}
            </div>
            <button
              onClick={() => setIdx(i => Math.min(previews.length - 1, i + 1))}
              disabled={idx === previews.length - 1}
              className="p-1 hover:bg-gray-200 rounded disabled:opacity-40"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-5 space-y-3">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-0.5">To</p>
              <p className="font-medium text-gray-900">{current.name}</p>
              <p className="text-gray-500 text-xs">{current.email}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-0.5">Subject</p>
              <p className="font-medium text-gray-900 text-sm">{current.subject}</p>
            </div>
          </div>

          <div className="border border-gray-200 rounded-xl p-4">
            <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">
              {current.body}
            </pre>
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800">
            ✉️ This email is personalized with {current.name.split(' ')[0]}'s specific experience and certifications. Each recipient receives a unique version.
          </div>
        </div>

        <div className="flex justify-between items-center p-4 border-t bg-gray-50 rounded-b-2xl">
          <p className="text-xs text-gray-500">
            {idx + 1} of {previews.length} — Sending all {previews.length} personalised email{previews.length > 1 ? 's' : ''}
          </p>
          <div className="flex gap-2">
            <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">
              Cancel
            </button>
            <button
              onClick={onSend}
              className="flex items-center gap-2 bg-emerald-600 text-white px-5 py-2 rounded-lg hover:bg-emerald-700 transition-colors font-medium text-sm"
            >
              <Send size={14} />
              Send {previews.length} Email{previews.length > 1 ? 's' : ''}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
