import { useEffect, useState } from 'react'

interface Props {
  score: number
  max: number
  animate?: boolean
}

export default function ScoreBar({ score, max, animate = true }: Props) {
  const [width, setWidth] = useState(0)
  const pct = Math.round((score / max) * 100)

  useEffect(() => {
    if (!animate) { setWidth(pct); return }
    const t = setTimeout(() => setWidth(pct), 100)
    return () => clearTimeout(t)
  }, [pct, animate])

  const color =
    pct >= 75 ? 'bg-emerald-500' :
    pct >= 55 ? 'bg-yellow-400' :
    pct >= 35 ? 'bg-orange-400' : 'bg-red-400'

  return (
    <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
      <div
        className={`h-2 rounded-full transition-all duration-700 ease-out ${color}`}
        style={{ width: `${width}%` }}
      />
    </div>
  )
}
