import { useEffect, useMemo, useState } from "react";
import { getAuthorsCached, compareAuthors } from "../api";

export default function Compare() {
  const [authors, setAuthors] = useState([]);
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const [result, setResult] = useState(null);
  const [err, setErr] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getAuthorsCached().then(setAuthors).catch(() => setErr(true));
  }, []);

  const options = useMemo(() => authors || [], [authors]);

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
  const authorA = useMemo(
    () => authors.find((x) => String(x.id) === String(a)),
    [authors, a]
    );

    const authorB = useMemo(
    () => authors.find((x) => String(x.id) === String(b)),
    [authors, b]
    );
  return (
    <div className="page">
      <h1 className="title">Compare Thinkers</h1>

      <div className="rule" />

      <div className="controls">
        <select className="input" value={a} onChange={(e) => setA(e.target.value)}>
          <option value="">Author A</option>
          {options.map((x) => (
            <option key={x.id} value={x.id}>{x.name}</option>
          ))}
        </select>

        <select className="input" value={b} onChange={(e) => setB(e.target.value)}>
          <option value="">Author B</option>
          {options.map((x) => (
            <option key={x.id} value={x.id}>{x.name}</option>
          ))}
        </select>

        <button
            className="button"
            onClick={run}
            disabled={!a || !b || a === b || loading}
            >
          {loading ? "Comparing…" : "Compare"}
        </button>
      </div>

      {err && <div className="meta mt12">Comparison failed.</div>}

      {result && (
        <>
            <div className="rule" />

            {/* SIDE-BY-SIDE COMPARISON */}
            <div
            style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                columnGap: "3rem",
                rowGap: "1.2rem",
                alignItems: "start",
            }}
            >
            {/* header */}
            <div className="h1">{authorA?.name || "Author A"}</div>
            <div className="h1">{authorB?.name || "Author B"}</div>

            {/* Topics */}
            <div className="h3">Primary unique topics</div>
            <div className="h3">Primary unique topics</div>

            <ul>
                {(result.unique_a || []).map((t, i) => <li key={i}>{t}</li>)}
            </ul>
            <ul>
                {(result.unique_b || []).map((t, i) => <li key={i}>{t}</li>)}
            </ul>

            {/* Shared */}
            <div className="h3">Shared topics</div>
            <div className="h3">Shared topics</div>

            <ul>
                {(result.shared_topics || []).map((t, i) => <li key={i}>{t}</li>)}
            </ul>
            <ul>
                {(result.shared_topics || []).map((t, i) => <li key={i}>{t}</li>)}
            </ul>
            </div>

            <div className="rule" />

            {/* DISAGREEMENTS — keep vertical (better for reading arguments) */}
            <section className="readable">
            <h2 className="h2">Direct disagreements</h2>

            {result.disagreement?.length ? (
                <ul>
                {result.disagreement.map((x, i) => (
                    <li key={i}>
                    <span className="mono">{x.claim_a}</span>
                    {"  ↔  "}
                    <span className="mono">{x.claim_b}</span>
                    </li>
                ))}
                </ul>
            ) : (
                <div className="meta">No explicit contradictions detected.</div>
            )}
            </section>

            <div className="rule" />

            {/* AGREEMENT — summarized last */}
            <section className="readable">
            <h2 className="h2">Shared beliefs</h2>
            {result.agreement?.length ? (
                <ul>
                {result.agreement.map((x, i) => (
                    <li key={i}>
                    <span className="mono">{x.canonical || x}</span>
                    </li>
                ))}
                </ul>
            ) : (
                <div className="meta">No strong agreement detected.</div>
            )}
            </section>
        </>
        )}
    </div>
  );
}