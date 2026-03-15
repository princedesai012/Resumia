import { useState } from 'react'
import UploadZone from './components/UploadZone'
import ScoreGauge from './components/ScoreGauge'
import SkillsPanel from './components/SkillsPanel'
import FeedbackPanel from './components/FeedbackPanel'
import './App.css'

// Use the environment variable if available (for production), otherwise fallback to localhost
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const TABS = ['Resume Profile', 'ATS Score', 'Strategic Feedback']

export default function App() {
  const [isLoading, setIsLoading]   = useState(false)
  const [activeTab, setActiveTab]   = useState(0)
  const [result, setResult]         = useState(null)
  const [error, setError]           = useState(null)
  const [timing, setTiming]         = useState(null)

  const handleAnalyze = async (file, role) => {
    setIsLoading(true)
    setError(null)
    setResult(null)
    setActiveTab(0)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_BASE}/api/analyze?job_role=${role}`, {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `Server error ${res.status}`)
      }

      const data = await res.json()
      setResult(data)
      setTiming(data.pipeline_duration_seconds)
      setActiveTab(1)  // Auto-navigate to ATS score after analysis
    } catch (err) {
      setError(err.message || 'Something went wrong. Is the backend running?')
    } finally {
      setIsLoading(false)
    }
  }

  const parsed   = result?.agents?.agent_1_parsed_resume
  const ats      = result?.agents?.agent_2_ats_compliance
  const feedback = result?.agents?.agent_3_strategic_feedback
  const ragMeta  = result?.rag_metadata

  return (
    <div className="app-layout">

      {/* ── Header ──────────────────────────────────── */}
      <header className="app-header">
        <div className="header-inner">
          <div className="header-brand">
            <div className="brand-logo">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.8">
                <path d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div>
              <h1 className="brand-name">Resumia</h1>
              <p className="brand-tagline">Autonomous Career Intelligence Agent</p>
            </div>
          </div>

          <div className="header-pills">
            <span className="tech-pill">LangChain</span>
            <span className="tech-pill">FAISS RAG</span>
            <span className="tech-pill">Gemini AI</span>
          </div>
        </div>
      </header>

      {/* ── Main Content ─────────────────────────────── */}
      <main className="app-main">
        <div className="content-grid">

          {/* ── LEFT PANEL: Upload ──────────────────── */}
          <aside className="left-panel">
            <div className="glass-card panel-card">
              <div className="panel-header">
                <span className="panel-title">Upload Resume</span>
                <span className="badge badge-violet">Agent Pipeline</span>
              </div>
              <div className="divider" />
              <div style={{ padding: '20px' }}>
                <UploadZone onAnalyze={handleAnalyze} isLoading={isLoading} />
              </div>
            </div>

            {/* Pipeline Status */}
            <div className="glass-card pipeline-status-card">
              <p className="panel-title" style={{ marginBottom: 14 }}>Pipeline Status</p>
              {[
                { label: 'Agent 1 — Structural Parser',   sublabel: 'FewShotPromptTemplate',        done: !!parsed,   active: isLoading && !parsed },
                { label: 'FAISS RAG Retrieval',           sublabel: 'text-embedding-004 + Vector DB', done: !!ats,     active: isLoading && !!parsed && !ats },
                { label: 'Agent 2 — ATS Compliance',      sublabel: 'ATS Rubric Scorer',             done: !!ats,      active: isLoading && !!parsed && !ats },
                { label: 'Agent 3 — Strategic Feedback',  sublabel: 'Career Coach Agent',            done: !!feedback, active: isLoading && !!ats && !feedback },
              ].map((step, i) => (
                <div key={i} className={`pipeline-step ${step.done ? 'done' : step.active ? 'active' : ''}`}>
                  <div className="pipeline-dot">
                    {step.done ? (
                      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                    ) : step.active ? (
                      <div className="spinner-dot"/>
                    ) : (
                      <div className="idle-dot"/>
                    )}
                  </div>
                  <div>
                    <p className="pipeline-step-label">{step.label}</p>
                    <p className="pipeline-step-sub">{step.sublabel}</p>
                  </div>
                </div>
              ))}

              {timing && (
                <p style={{ marginTop: 14, fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  ⏱ Completed in {timing}s
                </p>
              )}
              {ragMeta && (
                <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4, fontFamily: 'var(--font-mono)' }}>
                  🔍 {ragMeta.jd_chunks_retrieved} JD chunks via {ragMeta.vector_db}
                </p>
              )}
            </div>
          </aside>

          {/* ── RIGHT PANEL: Results ─────────────────── */}
          <section className="right-panel">

            {!result && !isLoading && !error && (
              <div className="empty-state animate-fadeIn">
                <div className="empty-icon animate-float">
                  <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="var(--brand-start)" strokeWidth="1">
                    <path d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h2 style={{ fontSize: 22, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 8 }}>Ready to Analyze</h2>
                <p style={{ fontSize: 14, color: 'var(--text-secondary)', maxWidth: 360, textAlign: 'center', lineHeight: 1.6 }}>
                  Upload your resume and select a target job role. The AI pipeline will run 3 autonomous agents to give you deep career intelligence.
                </p>
                <div style={{ display: 'flex', gap: 8, marginTop: 20 }}>
                  {['3-Agent Pipeline', 'FAISS RAG', 'ATS Scoring', 'Career Strategy'].map(t => (
                    <span key={t} className="badge badge-violet">{t}</span>
                  ))}
                </div>
              </div>
            )}

            {isLoading && !result && (
              <div className="loading-state animate-fadeIn">
                <div className="loading-spinner"/>
                <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 8 }}>Agents Working...</h2>
                <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>Running the 3-agent pipeline. This takes 15–30 seconds.</p>
                <div className="loading-steps">
                  {['Parsing resume structure', 'Embedding & FAISS retrieval', 'ATS compliance scoring', 'Generating career strategy'].map((s, i) => (
                    <div key={i} className="loading-step-item">
                      <div className="loading-step-dot" style={{ animationDelay: `${i * 0.3}s` }}/>
                      <span>{s}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {error && (
              <div className="error-state animate-fadeIn">
                <div className="error-icon">⚠️</div>
                <h2 style={{ fontWeight: 700, fontSize: 18, marginBottom: 8 }}>Analysis Failed</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{error}</p>
                <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 8 }}>Make sure the backend is running: <code style={{ fontFamily: 'var(--font-mono)' }}>uvicorn main:app --reload</code></p>
              </div>
            )}

            {result && (
              <div className="results-wrap animate-fadeInUp">
                {/* Candidate Header */}
                {parsed?.name && (
                  <div className="candidate-header">
                    <div className="candidate-avatar">
                      {parsed.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h2 className="candidate-name">{parsed.name}</h2>
                      <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                        {parsed.contact?.email && <span>{parsed.contact.email}</span>}
                        {parsed.contact?.location && <span> · {parsed.contact.location}</span>}
                        {parsed.total_experience_years > 0 && <span> · {parsed.total_experience_years}y experience</span>}
                      </p>
                    </div>
                    <div style={{ marginLeft: 'auto', display: 'flex', gap: 8, alignItems: 'center' }}>
                      {ats?.ats_grade && (
                        <span className={`badge ${
                          ats.ats_grade === 'A' ? 'badge-emerald' :
                          ats.ats_grade === 'B' ? 'badge-violet' :
                          ats.ats_grade === 'C' ? 'badge-amber' : 'badge-rose'
                        }`}>
                          ATS Grade: {ats.ats_grade}
                        </span>
                      )}
                      <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>→ {result.target_role}</span>
                    </div>
                  </div>
                )}

                {/* Tabs */}
                <div className="result-tabs">
                  {TABS.map((t, i) => (
                    <button
                      key={i}
                      className={`tab-btn ${activeTab === i ? 'active' : ''}`}
                      onClick={() => setActiveTab(i)}
                    >
                      {i === 0 && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 11a4 4 0 100-8 4 4 0 000 8z" strokeLinecap="round"/></svg>}
                      {i === 1 && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>}
                      {i === 2 && <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>}
                      {t}
                    </button>
                  ))}
                </div>

                {/* Tab Content */}
                <div className="glass-card tab-content-card">
                  {activeTab === 0 && <SkillsPanel parsedResume={parsed} atsData={ats} />}
                  {activeTab === 1 && <ScoreGauge atsData={ats} />}
                  {activeTab === 2 && <FeedbackPanel feedbackData={feedback} />}
                </div>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  )
}
