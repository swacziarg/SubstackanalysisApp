import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getProfileCached, api } from "../api";

export default function Profile() {
  const { authorId } = useParams();
  const [data, setData] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loadingAsk, setLoadingAsk] = useState(false);

  useEffect(() => {
    getProfileCached(authorId)
      .then(setData)
      .catch(() => setData({ error: true }));
  }, [authorId]);

  const askAuthor = async () => {
    if (!question.trim()) return;

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
    }

    setLoadingAsk(false);
  };

  if (!data) return <div>Loading belief profile...</div>;
  if (data.error) return <div>Failed to load profile.</div>;

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", lineHeight: 1.6 }}>
      <h1>Author Belief Profile</h1>

      <section>
        <h2>Worldview Summary</h2>
        <p>{data.summary || "Not enough data yet."}</p>
      </section>

      <section>
        <h2>Core Beliefs</h2>
        <ul>
          {data.beliefs?.length ? (
            data.beliefs.map((b, i) => <li key={i}>{b}</li>)
          ) : (
            <li>No recurring claims detected yet.</li>
          )}
        </ul>
      </section>

      <section>
        <h2>Recurring Topics</h2>
        <ul>
          {data.recurring_topics?.length ? (
            data.recurring_topics.map((t, i) => <li key={i}>{t}</li>)
          ) : (
            <li>No dominant topics yet.</li>
          )}
        </ul>
      </section>

      <section>
        <h2>Bias Overview</h2>
        <pre>{JSON.stringify(data.bias_overview, null, 2)}</pre>
      </section>

      <section style={{ marginTop: 40 }}>
        <h2>Ask this Author</h2>

        <div
          style={{
            border: "1px solid #ddd",
            borderRadius: 8,
            padding: 16,
            minHeight: 200,
            background: "#fafafa",
          }}
        >
          {messages.map((m, i) => (
            <div
              key={i}
              style={{
                marginBottom: 12,
                textAlign: m.role === "user" ? "right" : "left",
              }}
            >
              <div
                style={{
                  display: "inline-block",
                  padding: "8px 12px",
                  borderRadius: 12,
                  background: m.role === "user" ? "#d1e7ff" : "#eee",
                }}
              >
                {m.text}
              </div>
            </div>
          ))}
          {loadingAsk && <div>Thinking...</div>}
        </div>

        <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask about this author's views..."
            style={{ flex: 1, padding: 10 }}
            onKeyDown={(e) => e.key === "Enter" && askAuthor()}
          />
          <button onClick={askAuthor}>Ask</button>
        </div>
      </section>
    </div>
  );
}
