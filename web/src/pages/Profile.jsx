// src/pages/Profile.jsx
import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getProfileCached, api } from "../api";

/*
  NOTE: This route is not currently wired in src/main.jsx.
  Kept coherent with the design philosophy anyway.
*/

export default function Profile() {
  const { authorId } = useParams();
  const [data, setData] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loadingAsk, setLoadingAsk] = useState(false);
  const [err, setErr] = useState(false);

  useEffect(() => {
    if (!authorId) return;
    setErr(false);
    getProfileCached(authorId)
      .then(setData)
      .catch(() => setErr(true));
  }, [authorId]);

  const beliefs = useMemo(() => data?.beliefs || [], [data]);
  const topics = useMemo(() => data?.recurring_topics || [], [data]);

  const askAuthor = async () => {
    if (!question.trim() || !authorId) return;

    setLoadingAsk(true);
    setMessages((m) => [...m, { role: "user", text: question }]);
    try {
      const res = await api.post(`/authors/${authorId}/ask`, { question });
      setMessages((m) => [...m, { role: "assistant", text: res.data.answer }]);
      setQuestion("");
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: "Error contacting reasoning engine." },
      ]);
    } finally {
      setLoadingAsk(false);
    }
  };

  if (err) return <div className="page">Failed to load profile.</div>;
  if (!data) return <div className="page">Loading worldview…</div>;

  return (
    <div className="page">
      <div className="breadcrumbs">
        <Link to="/">Thinkers</Link>
        <span className="crumb-sep">›</span>
        <span>Profile</span>
      </div>

      <h1 className="title">Worldview</h1>

      <div className="split">
        {/* LEFT — SUMMARY */}
        <div>
          <section className="readable" aria-label="Summary">
            <h2 className="h2">Summary</h2>
            <p className="m0">{data.summary || "Not enough data yet."}</p>
          </section>

          <div className="rule" />

          <section className="readable" aria-label="Core beliefs">
            <h2 className="h2">Core beliefs</h2>
            {beliefs.length ? (
              <ul>
                {beliefs.map((b, i) => (
                  <li key={i}>{b}</li>
                ))}
              </ul>
            ) : (
              <div className="meta">No recurring claims detected yet.</div>
            )}
          </section>

          <div className="rule" />

          <section className="readable" aria-label="Recurring topics">
            <h2 className="h2">Recurring topics</h2>
            {topics.length ? (
              <ul>
                {topics.map((t, i) => (
                  <li key={i}>{t}</li>
                ))}
              </ul>
            ) : (
              <div className="meta">No dominant topics yet.</div>
            )}
          </section>

          <div className="rule" />

          <section className="readable" aria-label="Bias overview">
            <h2 className="h2">Bias tendencies</h2>
            {data.bias_overview ? (
              <pre className="pre">{JSON.stringify(data.bias_overview, null, 2)}</pre>
            ) : (
              <div className="meta">No bias overview available.</div>
            )}
          </section>
        </div>

        {/* RIGHT — DIALOGUE */}
        <aside className="analysis" aria-label="Dialogue">
          <h2 className="h2">Dialogue</h2>
          <div className="meta">
            Exploration only. No interface theatrics—just a transcript.
          </div>

          <div className="chat" aria-label="Transcript">
            {messages.length === 0 ? (
              <div className="meta mt12">Ask a question about this author's beliefs…</div>
            ) : (
              messages.map((m, i) => (
                <div key={i} className="msg">
                  <div className="who">{m.role === "user" ? "You" : "Model"}</div>
                  <p className={`text ${m.role === "assistant" ? "mono" : ""}`}>{m.text}</p>
                </div>
              ))
            )}

            {loadingAsk && (
              <div className="msg">
                <div className="who">Model</div>
                <p className="text mono">Thinking…</p>
              </div>
            )}
          </div>

          <div className="mt12">
            <input
              className="input"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What does this author believe about…"
              onKeyDown={(e) => e.key === "Enter" && askAuthor()}
            />
          </div>

          <div className="controls mt12">
            <button className="button" onClick={askAuthor} disabled={loadingAsk}>
              {loadingAsk ? "Thinking…" : "Ask"}
            </button>
            <button
              className="linkButton"
              type="button"
              onClick={() => {
                setQuestion("");
                setMessages([]);
              }}
            >
              Clear
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}