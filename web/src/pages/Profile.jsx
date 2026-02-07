import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getProfileCached, api } from "../api";

export default function Profile() {
  const { authorId } = useParams();

  const [data, setData] = useState(undefined);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loadingAsk, setLoadingAsk] = useState(false);

  const scrollRef = useRef(null);

  useEffect(() => {
    if (!authorId || authorId === "undefined") return;
    getProfileCached(authorId)
      .then(setData)
      .catch(() => setData(null));
  }, [authorId]);

  useEffect(() => {
    if (scrollRef.current)
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, loadingAsk]);

  async function askAuthor(text) {
    if (!text.trim() || loadingAsk) return;

    setQuestion("");
    setLoadingAsk(true);

    setMessages((m) => [...m, { role: "question", text }]);

    try {
      const res = await api.post(`/authors/${authorId}/ask`, { question: text });
      setMessages((m) => [...m, { role: "answer", text: res.data.answer }]);
    } catch {
      setMessages((m) => [...m, { role: "answer", text: "The model could not produce an answer." }]);
    } finally {
      setLoadingAsk(false);
    }
  }

  if (data === undefined) return <div className="page">Loading…</div>;
  if (data === null) return <div className="page">Failed to load worldview.</div>;

  const suggestions = [
    "What assumptions guide this author's thinking?",
    "Where would this author disagree with mainstream opinion?",
    "What does this author optimize for?",
    "What do they consistently misunderstand?",
  ];

  return (
    <div className="page">
      <div className="breadcrumbs">
        <Link to="/authors">Thinkers</Link>
        <span className="crumb-sep">›</span>
        <Link to={`/authors/${authorId}`}>Author</Link>
        <span className="crumb-sep">›</span>
        <span>Dialogue</span>
      </div>

      <h1 className="title">Dialogue</h1>

      {/* short explanation */}
      <p className="meta" style={{ maxWidth: "70ch" }}>
        You are questioning a reasoning model grounded in this author's writings.
        It answers normally for general knowledge, and uses the author's beliefs when relevant.
      </p>

      {/* transcript window */}
      <div
        ref={scrollRef}
        style={{
          height: "55vh",
          overflowY: "auto",
          borderTop: "1px solid var(--rule)",
          borderBottom: "1px solid var(--rule)",
          paddingTop: "12px",
          paddingBottom: "12px",
        }}
      >
        {messages.length === 0 && (
          <div className="meta">
            Suggested starting questions:
            <ul>
              {suggestions.map((s, i) => (
                <li key={i}>
                  <button className="linkButton" onClick={() => askAuthor(s)}>
                    {s}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className="msg">
            <div className="who">{m.role === "question" ? "You" : "Model"}</div>
            <p className={`text ${m.role === "answer" ? "mono" : ""}`}>{m.text}</p>
          </div>
        ))}

        {loadingAsk && (
          <div className="msg">
            <div className="who">Model</div>
            <p className="text mono">Thinking…</p>
          </div>
        )}
      </div>

      {/* input always visible */}
      <div className="mt12" style={{ maxWidth: "70ch" }}>
        <input
          className="input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question…"
          onKeyDown={(e) => e.key === "Enter" && askAuthor(question)}
        />
      </div>
    </div>
  );
}