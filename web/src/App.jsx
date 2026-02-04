import React, { useEffect, useMemo, useRef, useState } from 'react'

const TOTAL_QUESTIONS = 54
const TIME_LIMIT_SECONDS = 135 * 60
const LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

function fmtMMSS(totalSeconds) {
  const m = String(Math.floor(totalSeconds / 60)).padStart(2, '0')
  const s = String(totalSeconds % 60).padStart(2, '0')
  return `${m}:${s}`
}

function dedupeByPrompt(arr) {
  const seen = new Set()
  const out = []
  for (const q of arr) {
    if (!q?.prompt || seen.has(q.prompt)) continue
    seen.add(q.prompt)
    out.push(q)
  }
  return out
}

function shuffle(a) {
  const arr = [...a]
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[arr[i], arr[j]] = [arr[j], arr[i]]
  }
  return arr
}

function isMultiSelect(q) {
  return (q.correct?.length ?? 0) > 1
}

function pct(correct, attempted) {
  return attempted ? (correct / attempted) * 100 : 0
}

function nowIsoLocal() {
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem('ppx_history') || '[]')
  } catch {
    return []
  }
}

function saveHistory(rows) {
  localStorage.setItem('ppx_history', JSON.stringify(rows))
}

function LineChart({ values }) {
  if (!values?.length) return null
  const w = 320
  const h = 120
  const pad = 12

  const points = values.map((v, i) => {
    const x = pad + (i * (w - pad * 2)) / Math.max(1, values.length - 1)
    const y = h - pad - (v * (h - pad * 2)) / 100
    return [x, y]
  })

  const d = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ')
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ width: '100%', maxWidth: w }}>
      <rect x="0" y="0" width={w} height={h} rx="10" fill="#fff" />
      {[0, 25, 50, 75, 100].map((g) => {
        const y = h - pad - (g * (h - pad * 2)) / 100
        return <line key={g} x1={pad} x2={w - pad} y1={y} y2={y} stroke="#e6e8ee" strokeWidth="1" />
      })}
      <path d={d} fill="none" stroke="#111" strokeWidth="2" />
      {points.map((p, i) => (
        <circle key={i} cx={p[0]} cy={p[1]} r="3" fill="#111" />
      ))}
    </svg>
  )
}

export default function App() {
  const [loading, setLoading] = useState(true)
  const [bank, setBank] = useState([])
  const [exam, setExam] = useState([])
  const [idx, setIdx] = useState(0)
  const [selected, setSelected] = useState(new Set())
  const [locked, setLocked] = useState(false)
  const [correctCount, setCorrectCount] = useState(0)
  const [attempted, setAttempted] = useState(0)
  const [startTs, setStartTs] = useState(null)
  const [timeLeft, setTimeLeft] = useState(TIME_LIMIT_SECONDS)
  const [history, setHistory] = useState(loadHistory())
  const timerRef = useRef(null)

  useEffect(() => {
    async function load() {
      setLoading(true)
      try {
        const res = await fetch('./questions.json')
        const data = await res.json()
        setBank(dedupeByPrompt(Array.isArray(data) ? data : []))
      } catch (e) {
        console.error(e)
        setBank([])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  function startExam() {
    const pick = shuffle(bank).slice(0, Math.min(TOTAL_QUESTIONS, bank.length))
    setExam(pick)
    setIdx(0)
    setSelected(new Set())
    setLocked(false)
    setCorrectCount(0)
    setAttempted(0)
    const now = Date.now()
    setStartTs(now)
    setTimeLeft(TIME_LIMIT_SECONDS)
  }

  useEffect(() => {
    if (!startTs) return
    if (timerRef.current) clearInterval(timerRef.current)
    timerRef.current = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTs) / 1000)
      setTimeLeft(Math.max(0, TIME_LIMIT_SECONDS - elapsed))
    }, 250)
    return () => timerRef.current && clearInterval(timerRef.current)
  }, [startTs])

  useEffect(() => {
    if (startTs && timeLeft <= 0) setLocked(true)
  }, [timeLeft, startTs])

  const q = exam[idx]
  const isDone = useMemo(() => {
    if (!startTs) return false
    if (timeLeft <= 0) return true
    return idx >= exam.length
  }, [startTs, timeLeft, idx, exam.length])

  function toggleOption(optIdx) {
    if (!q || locked) return
    const ms = isMultiSelect(q)
    setSelected((prev) => {
      const next = new Set(prev)
      if (!ms) {
        next.clear()
        next.add(optIdx)
        return next
      }
      next.has(optIdx) ? next.delete(optIdx) : next.add(optIdx)
      return next
    })
  }

  function submitAnswer() {
    if (!q || locked || !selected.size) return
    setLocked(true)
    const corr = new Set(q.correct || [])
    const ok = corr.size === selected.size && [...corr].every((x) => selected.has(x))
    setAttempted((a) => a + 1)
    if (ok) setCorrectCount((c) => c + 1)
  }

  function nextQuestion() {
    setLocked(false)
    setSelected(new Set())
    setIdx((i) => i + 1)
  }

  function finishAndLog() {
    const durationSec = startTs ? Math.floor((Date.now() - startTs) / 1000) : 0
    const row = {
      timestamp: nowIsoLocal(),
      attempted,
      correct: correctCount,
      score_pct: Number(pct(correctCount, attempted).toFixed(2)),
      duration_sec: durationSec,
      total_questions: exam.length,
    }
    const next = [row, ...history].slice(0, 200)
    setHistory(next)
    saveHistory(next)
    setStartTs(null)
    setExam([])
    setIdx(0)
    setSelected(new Set())
    setLocked(false)
    setTimeLeft(TIME_LIMIT_SECONDS)
  }

  function exportCsv() {
    const header = ['timestamp','attempted','correct','score_pct','duration_sec','total_questions']
    const lines = [header.join(',')]
    for (const r of history) {
      const row = [r.timestamp, r.attempted, r.correct, r.score_pct, r.duration_sec, r.total_questions]
      lines.push(row.map(String).map(v => `"${v.replaceAll('"','""')}"`).join(','))
    }
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'practice_results.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  const scores = history.slice().reverse().map((r) => r.score_pct)

  return (
    <div className="wrap">
      <header className="top">
        <div>
          <h1>Python Practice Exam</h1>
          <p className="sub">54 questions • 135 min • mobile-friendly</p>
        </div>
        <div className="pillRow">
          <span className="pill">Bank: {bank.length} q</span>
          {startTs && <span className="pill">Time left: {fmtMMSS(timeLeft)}</span>}
        </div>
      </header>

      <main className="card">
        {loading && <p>Loading questions…</p>}

        {!loading && bank.length === 0 && (
          <div>
            <p><b>No questions loaded.</b></p>
            <p>Make sure <code>public/questions.json</code> exists and is valid JSON.</p>
          </div>
        )}

        {!loading && bank.length > 0 && !startTs && (
          <div className="start">
            <button className="btn" onClick={startExam}>Start Practice</button>
            <p className="hint">Tip: On your phone, open the site and “Add to Home Screen.”</p>

            <section className="history">
              <div className="historyHead">
                <h2>Progress</h2>
                <button className="btn ghost" onClick={exportCsv} disabled={!history.length}>Export CSV</button>
              </div>
              <LineChart values={scores} />
              {!history.length ? (
                <p className="muted">No attempts yet.</p>
              ) : (
                <div className="table">
                  <div className="row head">
                    <div>When</div><div>Score</div><div>Attempted</div><div>Duration</div>
                  </div>
                  {history.slice(0, 8).map((r, i) => (
                    <div key={i} className="row">
                      <div className="mono">{r.timestamp}</div>
                      <div><b>{r.score_pct}%</b></div>
                      <div>{r.correct}/{r.attempted}</div>
                      <div>{Math.floor(r.duration_sec/60)}m</div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        )}

        {startTs && !isDone && q && (
          <div className="quiz">
            <div className="qmeta">
              <span className="pill">Q {idx + 1} / {exam.length}</span>
              <span className="pill">Topic: {q.topic || 'General'}</span>
              <span className="pill">Score: {correctCount}/{attempted}</span>
            </div>

            <pre className="prompt">{q.prompt}</pre>

            <div className="opts">
              {q.options.map((opt, oi) => {
                const chosen = selected.has(oi)
                const corr = (q.correct || []).includes(oi)
                const show = locked
                return (
                  <button
                    key={oi}
                    className={[
                      'opt',
                      chosen ? 'chosen' : '',
                      show && corr ? 'correct' : '',
                      show && chosen && !corr ? 'wrong' : '',
                    ].join(' ').trim()}
                    onClick={() => toggleOption(oi)}
                    disabled={locked || timeLeft <= 0}
                  >
                    <span className="letter">{LETTERS[oi]}</span>
                    <span className="optText">{opt}</span>
                  </button>
                )
              })}
            </div>

            <div className="actions">
              {!locked ? (
                <button className="btn" onClick={submitAnswer} disabled={!selected.size || timeLeft <= 0}>
                  Submit
                </button>
              ) : (
                <button className="btn" onClick={nextQuestion}>
                  Next
                </button>
              )}
            </div>

            {locked && (
              <div className="explain">
                <h3>Explanation</h3>
                {(q.options || []).map((opt, oi) => {
                  const isC = (q.correct || []).includes(oi)
                  const why = q.explanations?.[String(oi)] ?? 'No explanation provided.'
                  return (
                    <div key={oi} className="exRow">
                      <div className="mono"><b>{LETTERS[oi]}.</b> {opt}</div>
                      <div className={isC ? 'good' : 'bad'}>
                        <b>{isC ? 'CORRECT' : 'WRONG'}:</b> {why}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}

        {startTs && (isDone || idx >= exam.length) && (
          <div className="done">
            <h2>Done</h2>
            <p><b>Score:</b> {correctCount}/{attempted} ({pct(correctCount, attempted).toFixed(1)}%)</p>
            <p className="muted">Attempts are saved locally in your browser (localStorage).</p>
            <div className="actions">
              <button className="btn" onClick={finishAndLog}>Save Attempt</button>
              <button className="btn ghost" onClick={() => { setStartTs(null); setExam([]); }}>Back</button>
            </div>
          </div>
        )}
      </main>

      <footer className="foot">
        <span className="muted">Hosted via GitHub Pages • Export CSV available</span>
      </footer>
    </div>
  )
}
