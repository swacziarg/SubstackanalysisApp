// src/pages/Compare.jsx
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { compareAuthors, getAuthorsCached } from "../api";

export default function Compare() {
  const [authors, setAuthors] = useState([]);
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const [result, setResult] = useState(null);
  const [err, setErr] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getAuthorsCached()
      .then(setAuthors)
      .catch(() => setErr(true));
  }, []);

  const authorOptions = useMemo(() => authors || [], [authors]);

  const run = async () => {
    if (!a || !b) return;
    setErr(false);
    setLoading(true);
    setResult(null);
    try {
      const r = await compareAuthors(a, b);
      setResult(r.data);
    } catch {
      setErr(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="breadcrumbs">
        <Link to="/">Thinkers</Link>
        <span className="crumb-sep">›</span>
        <span>Compare</span>
      </div>

      <h1 className="title">Compare</h1>
      <div className="meta readable">
        One question: how do two thinkers differ? Minimal controls; maximal legibility.
      </div>

      <div className="rule" />

      <div className="readable" aria-label="Compare controls">
        <div className="h3">Select two authors</div>
        <div className="controls mt8">
          <select className="input" value={a} onChange={(e) => setA(e.target.value)}>
            <option value="">Author A</option>
            {authorOptions.map((x) => (
              <option key={x.id} value={x.id}>
                {x.name}
              </option>
            ))}
          </select>

          <select className="input" value={b} onChange={(e) => setB(e.target.value)}>
            <option value="">Author B</option>
            {authorOptions.map((x) => (
              <option key={x.id} value={x.id}>
                {x.name}
              </option>
            ))}
          </select>

          <button className="button" onClick={run} disabled={loading || !a || !b}>
            {loading ? "Comparing…" : "Compare"}
          </button>

          <button
            className="linkButton"
            type="button"
            onClick={() => {
              setA("");
              setB("");
              setResult(null);
              setErr(false);
            }}
          >
            Clear
          </button>
        </div>

        {err && <div className="meta mt12">Failed to compare authors.</div>}
      </div>

      {result && (
        <>
          <div className="rule" />
          <div className="readable" aria-label="Comparison result">
            <h2 className="h2">Agreement</h2>
            {Array.isArray(result.agreement) && result.agreement.length > 0 ? (
              <ul>
                {result.agreement.map((x, i) => (
                  <li key={i}>
                    <span style={{ fontFamily: "var(--mono)", fontSize: "0.95rem" }}>
                      {x.canonical || String(x)}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="meta">No agreement entries returned.</div>
            )}
          </div>
        </>
      )}
    </div>
  );
}