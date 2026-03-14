import { useEffect, useState } from 'react'
import './ScoreGauge.css'

const SCORE_COLORS = {
  A: { stroke: '#10b981', text: '#10b981', fill: 'rgba(16,185,129,0.1)' },
  B: { stroke: '#6366f1', text: '#6366f1', fill: 'rgba(99,102,241,0.1)' },
  C: { stroke: '#f59e0b', text: '#f59e0b', fill: 'rgba(245,158,11,0.1)' },
  D: { stroke: '#f97316', text: '#f97316', fill: 'rgba(249,115,22,0.1)' },
  F: { stroke: '#f43f5e', text: '#f43f5e', fill: 'rgba(244,63,94,0.1)' },
}

const DIMENSION_LABELS = {
  keyword_match:             { label: 'Keyword Match',   color: '#6366f1', weight: '35%' },
  action_verbs:              { label: 'Action Verbs',    color: '#8b5cf6', weight: '20%' },
  quantified_achievements:   { label: 'Achievements',    color: '#06b6d4', weight: '25%' },
  section_completeness:      { label: 'Completeness',    color: '#10b981', weight: '10%' },
  format_compliance:         { label: 'ATS Format',      color: '#f59e0b', weight: '10%' },
}

export default function ScoreGauge({ atsData }) {
  const [animated, setAnimated] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 100)
    return () => clearTimeout(t)
  }, [atsData])

  if (!atsData) return null

  const score = atsData.total_ats_score ?? 0
  const grade = atsData.ats_grade ?? 'F'
  const pass  = atsData.pass_threshold ?? false
  const dims  = atsData.dimensions ?? {}
  const colors = SCORE_COLORS[grade] || SCORE_COLORS.F

  // SVG ring math
  const R = 70, CX = 90, CY = 90
  const circ = 2 * Math.PI * R
  const offset = animated ? circ - (score / 100) * circ : circ

  return (
    <div className="score-gauge-wrap">

      {/* Circular Score Ring */}
      <div style={{ position: 'relative' }}>
        <svg width="180" height="180" className="score-gauge-svg">
          <defs>
            <linearGradient id="ring-grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={colors.stroke} />
              <stop offset="100%" stopColor={colors.stroke + 'aa'} />
            </linearGradient>
          </defs>
          {/* Track */}
          <circle cx={CX} cy={CY} r={R} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="10"/>
          {/* Score ring */}
          <circle
            className="progress-ring-circle"
            cx={CX} cy={CY} r={R}
            fill="none"
            stroke={`url(#ring-grad)`}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            style={{ filter: `drop-shadow(0 0 8px ${colors.stroke}66)` }}
          />
          {/* Center content */}
          <text x={CX} y={CY - 8} className="score-center-text score-number" fill={colors.text}>{Math.round(score)}</text>
          <text x={CX} y={CY + 16} className="score-center-text score-label-svg">ATS SCORE</text>
        </svg>
      </div>

      {/* Grade + Pass/Fail */}
      <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
        <div className="score-grade-badge" style={{ background: colors.fill, color: colors.text, border: `1px solid ${colors.stroke}44` }}>
          {grade}
        </div>
        <span className={`badge ${pass ? 'badge-emerald' : 'badge-rose'}`}>
          {pass ? '✓ ATS PASS' : '✗ ATS FAIL'}
        </span>
      </div>

      <div className="divider" style={{ width: '100%' }} />

      {/* Dimension Breakdown */}
      <div className="score-dimensions" style={{ width: '100%' }}>
        {Object.entries(DIMENSION_LABELS).map(([key, meta]) => {
          const dimScore = dims[key]?.score ?? 0
          return (
            <div key={key} className="dimension-row">
              <div className="dimension-header">
                <span className="dimension-name">{meta.label}</span>
                <span className="dimension-score" style={{ color: meta.color }}>{Math.round(dimScore)}</span>
              </div>
              <div className="dimension-bar-track">
                <div
                  className="dimension-bar-fill"
                  style={{
                    width: animated ? `${dimScore}%` : '0%',
                    background: `linear-gradient(90deg, ${meta.color}cc, ${meta.color})`,
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
