import './Panels.css'

const PRIORITY_META = {
  HIGH:   { color: '#f43f5e', bg: 'rgba(244,63,94,0.1)',  border: 'rgba(244,63,94,0.25)',  icon: '🔴' },
  MEDIUM: { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.25)', icon: '🟡' },
  LOW:    { color: '#6366f1', bg: 'rgba(99,102,241,0.1)', border: 'rgba(99,102,241,0.25)', icon: '🔵' },
}

export default function FeedbackPanel({ feedbackData }) {
  if (!feedbackData) return null

  const verdict     = feedbackData.overall_verdict ?? ''
  const probability = feedbackData.interview_probability ?? 'Unknown'
  const skillGap    = feedbackData.skill_gap_analysis ?? {}
  const narrative   = feedbackData.narrative_assessment ?? {}
  const improvements = feedbackData.prioritized_improvements ?? []
  const quickWins   = feedbackData.quick_wins ?? []
  const roadmap     = feedbackData.skill_development_roadmap ?? {}
  const rewrites    = feedbackData.rewrite_suggestions ?? []

  const probColor = probability === 'High' ? '#10b981' : probability === 'Medium' ? '#f59e0b' : '#f43f5e'

  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: 0 }}>

      {/* Verdict Banner */}
      <div style={{
        padding: '16px',
        borderRadius: 'var(--radius-md)',
        background: 'rgba(99,102,241,0.06)',
        border: '1px solid rgba(99,102,241,0.20)',
        marginBottom: 20
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>AI Verdict</span>
          <span className="badge" style={{ background: `${probColor}18`, color: probColor, border: `1px solid ${probColor}44` }}>
            {probability} Interview Chance
          </span>
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{verdict}</p>
      </div>

      {/* Skill Gap */}
      {(skillGap.critical_missing?.length > 0 || skillGap.strong_matches?.length > 0) && (
        <div className="panel-section">
          <p className="panel-section-title">Skill Gap Analysis</p>
          {skillGap.critical_missing?.length > 0 && (
            <div style={{ marginBottom: 10 }}>
              <p style={{ fontSize: 11, color: 'var(--accent-rose)', fontWeight: 700, marginBottom: 6, textTransform: 'uppercase' }}>⚠ Critical Gaps</p>
              <div className="tags-wrap">
                {skillGap.critical_missing.map((s, i) => <span key={i} className="tag-chip missing">{s}</span>)}
              </div>
            </div>
          )}
          {skillGap.nice_to_have_missing?.length > 0 && (
            <div style={{ marginBottom: 10 }}>
              <p style={{ fontSize: 11, color: 'var(--accent-amber)', fontWeight: 700, marginBottom: 6, textTransform: 'uppercase' }}>• Nice to Have</p>
              <div className="tags-wrap">
                {skillGap.nice_to_have_missing.map((s, i) => <span key={i} className="tag-chip" style={{ borderColor: 'rgba(245,158,11,0.3)', color: '#f59e0b' }}>{s}</span>)}
              </div>
            </div>
          )}
          {skillGap.strong_matches?.length > 0 && (
            <div>
              <p style={{ fontSize: 11, color: 'var(--accent-emerald)', fontWeight: 700, marginBottom: 6, textTransform: 'uppercase' }}>✓ Strong Matches</p>
              <div className="tags-wrap">
                {skillGap.strong_matches.map((s, i) => <span key={i} className="tag-chip matched">{s}</span>)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Narrative Assessment */}
      {narrative.summary_feedback && (
        <div className="panel-section">
          <p className="panel-section-title">Narrative Assessment</p>
          <div style={{ padding: '12px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Summary Strength: </span>
            <span style={{ fontSize: 12, fontWeight: 700, color: narrative.summary_strength === 'Strong' ? 'var(--accent-emerald)' : narrative.summary_strength === 'Moderate' ? 'var(--accent-amber)' : 'var(--accent-rose)' }}>
              {narrative.summary_strength}
            </span>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 8, lineHeight: 1.5 }}>{narrative.summary_feedback}</p>
          </div>
        </div>
      )}

      {/* Prioritized Improvements */}
      {improvements.length > 0 && (
        <div className="panel-section">
          <p className="panel-section-title">Prioritized Improvements</p>
          {improvements.map((imp, i) => {
            const meta = PRIORITY_META[imp.priority] || PRIORITY_META.LOW
            return (
              <div key={i} className="improvement-card" style={{ borderLeft: `3px solid ${meta.color}` }}>
                <div className="improvement-header">
                  <span className="badge" style={{ background: meta.bg, color: meta.color, border: `1px solid ${meta.border}` }}>
                    {imp.priority}
                  </span>
                  <span className="improvement-category">{imp.category}</span>
                </div>
                <p className="improvement-issue">{imp.issue}</p>
                <p className="improvement-action">→ {imp.action}</p>
                {imp.example && (
                  <div className="improvement-example">{imp.example}</div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Quick Wins */}
      {quickWins.length > 0 && (
        <div className="panel-section">
          <p className="panel-section-title">⚡ Quick Wins (Under 1 Hour)</p>
          {quickWins.map((qw, i) => (
            <div key={i} className="quick-win-row">
              <div className="quick-win-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--brand-start)" strokeWidth="2">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                </svg>
              </div>
              <p className="quick-win-desc">{qw.description}</p>
              <span className="quick-win-time">{qw.time_required}</span>
            </div>
          ))}
        </div>
      )}

      {/* Rewrite Suggestions */}
      {rewrites.length > 0 && (
        <div className="panel-section">
          <p className="panel-section-title">✍ Bullet Rewrites</p>
          {rewrites.slice(0, 3).map((rw, i) => (
            <div key={i} className="rewrite-card">
              <div className="rewrite-before">
                <p className="rewrite-label" style={{ color: 'var(--accent-rose)' }}>Before</p>
                {rw.original_bullet}
              </div>
              <div className="rewrite-after">
                <p className="rewrite-label" style={{ color: 'var(--accent-emerald)' }}>After</p>
                {rw.improved_bullet}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 30/60/90 Roadmap */}
      {(roadmap['30_days']?.length > 0 || roadmap['60_days']?.length > 0 || roadmap['90_days']?.length > 0) && (
        <div className="panel-section">
          <p className="panel-section-title">📅 30 / 60 / 90 Day Roadmap</p>
          <div className="roadmap-grid">
            {[
              { key: '30_days', label: '30 Days', color: '#10b981' },
              { key: '60_days', label: '60 Days', color: '#6366f1' },
              { key: '90_days', label: '90 Days', color: '#8b5cf6' },
            ].map(col => (
              <div key={col.key} className="roadmap-col" style={{ borderTop: `2px solid ${col.color}` }}>
                <p className="roadmap-col-title" style={{ color: col.color }}>{col.label}</p>
                {(roadmap[col.key] ?? []).map((item, i) => (
                  <p key={i} className="roadmap-item">{item}</p>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  )
}
