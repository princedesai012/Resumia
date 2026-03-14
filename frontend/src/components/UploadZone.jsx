import { useState, useRef } from 'react'
import './UploadZone.css'

const ROLES = [
  { value: 'software_engineer', label: '💻 Software Engineer' },
  { value: 'data_scientist',    label: '🤖 Data Scientist / ML Engineer' },
  { value: 'product_manager',   label: '📊 Product Manager' },
]

const formatBytes = (bytes) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

export default function UploadZone({ onAnalyze, isLoading }) {
  const [dragOver, setDragOver] = useState(false)
  const [file, setFile] = useState(null)
  const [role, setRole] = useState('software_engineer')
  const inputRef = useRef(null)

  const handleFile = (f) => {
    if (!f) return
    const allowed = ['.pdf', '.txt', '.doc', '.docx']
    const ext = '.' + f.name.split('.').pop().toLowerCase()
    if (!allowed.includes(ext)) {
      alert('Please upload a PDF, DOCX, DOC, or TXT file.')
      return
    }
    if (f.size > 5 * 1024 * 1024) {
      alert('File must be under 5MB.')
      return
    }
    setFile(f)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  const handleAnalyze = () => {
    if (file && onAnalyze) onAnalyze(file, role)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Dropzone */}
      <div
        className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
        onClick={() => !file && inputRef.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt,.doc,.docx"
          style={{ display: 'none' }}
          onChange={(e) => handleFile(e.target.files[0])}
        />

        <div className="upload-icon-wrap" style={{ margin: '0 auto 20px' }}>
          <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>

        {!file ? (
          <>
            <p className="upload-title">Drop your resume here</p>
            <p className="upload-subtitle">or click to browse your files</p>
            <p className="upload-hint">PDF, DOCX, or TXT · Max 5MB</p>
          </>
        ) : (
          <div className="upload-file-preview" onClick={(e) => e.stopPropagation()}>
            <svg className="file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <div style={{ flex: 1, minWidth: 0 }}>
              <p className="file-name">{file.name}</p>
              <p className="file-size">{formatBytes(file.size)}</p>
            </div>
            <button className="file-remove" onClick={(e) => { e.stopPropagation(); setFile(null) }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        )}
      </div>

      {/* Role Selector */}
      <div>
        <label className="role-selector-label">Target Job Role</label>
        <select className="role-selector" value={role} onChange={(e) => setRole(e.target.value)}>
          {ROLES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
        </select>
      </div>

      {/* Analyze Button */}
      <button
        className="btn btn-primary"
        style={{ width: '100%', padding: '14px', fontSize: '15px', fontWeight: 700 }}
        onClick={handleAnalyze}
        disabled={!file || isLoading}
      >
        {isLoading ? (
          <>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ animation: 'spin 1s linear infinite' }}>
              <path d="M21 12a9 9 0 11-6.219-8.56" strokeLinecap="round"/>
            </svg>
            Analyzing Resume...
          </>
        ) : (
          <>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            Analyze Resume
          </>
        )}
      </button>
    </div>
  )
}
