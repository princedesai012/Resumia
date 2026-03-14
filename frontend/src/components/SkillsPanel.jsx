import './Panels.css'

export default function SkillsPanel({ parsedResume, atsData }) {
  if (!parsedResume) return null

  const skills = parsedResume.skills ?? {}
  const keywords = parsedResume.keywords ?? []
  const dims = atsData?.dimensions ?? {}
  const matched = dims.keyword_match?.matched_keywords ?? []
  const missing = dims.keyword_match?.missing_keywords ?? []
  const topMissing = dims.keyword_match?.top_missing_by_impact ?? missing.slice(0, 5)
  const allSkills = [
    ...(skills.languages ?? []),
    ...(skills.frameworks ?? []),
    ...(skills.databases ?? []),
    ...(skills.cloud_devops ?? []),
    ...(skills.data_tools ?? []),
    ...(skills.vector_databases ?? []),
  ]

  const getChipClass = (skill) => {
    const s = skill.toLowerCase()
    if (matched.some(m => m.toLowerCase().includes(s) || s.includes(m.toLowerCase()))) return 'matched'
    if (missing.some(m => m.toLowerCase().includes(s) || s.includes(m.toLowerCase()))) return 'missing'
    return ''
  }

  const exp = parsedResume.experience ?? []
  const edu = parsedResume.education ?? []
  const certs = parsedResume.certifications ?? []
  const totalYears = parsedResume.total_experience_years ?? 0

  return (
    <div style={{ padding: '20px' }}>

      {/* Quick Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginBottom: 24 }}>
        {[
          { label: 'Experience', value: `${totalYears}y`,   color: '#6366f1' },
          { label: 'Skills',     value: allSkills.length,   color: '#10b981' },
          { label: 'Roles',      value: exp.length,         color: '#f59e0b' },
        ].map(s => (
          <div key={s.label} style={{ textAlign: 'center', padding: '12px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: 22, fontWeight: 800, color: s.color, fontFamily: 'var(--font-mono)' }}>{s.value}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* All Skills */}
      {allSkills.length > 0 && (
        <div className="panel-section">
          <p className="panel-section-title">Skills Detected</p>
          <div className="tags-wrap">
            {allSkills.map((s, i) => (
              <span key={i} className={`tag-chip ${getChipClass(s)}`}>{s}</span>
            ))}
          </div>
          {(matched.length > 0 || missing.length > 0) && (
            <p style={{ marginTop: 8, fontSize: 11, color: 'var(--text-muted)' }}>
              <span style={{ color: 'var(--accent-emerald)' }}>● Green</span> = JD match &nbsp;
              <span style={{ color: 'var(--accent-rose)' }}>● Red</span> = JD mismatch
            </p>
          )}
        </div>
      )}

      {/* Top Missing Keywords */}
      {topMissing.length > 0 && (
        <div className="panel-section">
          <p className="panel-section-title">⚡ Critical Missing Keywords</p>
          <div className="tags-wrap">
            {topMissing.map((k, i) => (
              <span key={i} className="tag-chip missing">+ {k}</span>
            ))}
          </div>
        </div>
      )}

      {/* Experience */}
      {exp.length > 0 && (
        <div className="panel-section">
          <p className="panel-section-title">Experience</p>
          {exp.map((e, i) => (
            <div key={i} style={{ padding: '12px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', marginBottom: 8 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
                <div>
                  <p style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{e.title}</p>
                  <p style={{ fontSize: 12, color: 'var(--brand-start)' }}>{e.company}</p>
                </div>
                <span style={{ fontSize: 11, color: 'var(--text-muted)', whiteSpace: 'nowrap', marginLeft: 8, fontFamily: 'var(--font-mono)' }}>{e.duration}</span>
              </div>
              {(e.achievements ?? []).slice(0, 2).map((a, j) => (
                <p key={j} style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4, paddingLeft: 12, borderLeft: '2px solid var(--border-brand)', lineHeight: 1.4 }}>{a}</p>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Education */}
      {edu.length > 0 && (
        <div className="panel-section">
          <p className="panel-section-title">Education</p>
          {edu.map((e, i) => (
            <div key={i} style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 6 }}>
              <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{e.degree} in {e.field}</span>
              <span style={{ color: 'var(--text-muted)' }}> · {e.institution} {e.graduation_year ? `(${e.graduation_year})` : ''}</span>
            </div>
          ))}
        </div>
      )}

      {/* Certifications */}
      {certs.length > 0 && (
        <div className="panel-section">
          <p className="panel-section-title">Certifications</p>
          <div className="tags-wrap">
            {certs.map((c, i) => <span key={i} className="tag-chip">{c}</span>)}
          </div>
        </div>
      )}

    </div>
  )
}
