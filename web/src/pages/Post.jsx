// src/pages/Post.jsx
import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import DOMPurify from "dompurify";
import { getPostCached, api } from "../api";
import { peek } from "../store/fetchOnce";
import "../article.css";

export default function Post() {
  const { id } = useParams();
  const [post, setPost] = useState(() => peek(`post:${id}`));
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [askErr, setAskErr] = useState(false);

  useEffect(() => {
    getPostCached(id).then(setPost);
  }, [id]);

  const cleanHTML = useMemo(() => {
    return DOMPurify.sanitize(post?.html || "");
  }, [post]);

  async function ask() {
    if (!question.trim()) return;
    setAskErr(false);
    setLoading(true);
    setAnswer(null);
    try {
      const res = await api.post(`/posts/${id}/ask`, { question });
      setAnswer(res.data);
    } catch {
      setAskErr(true);
    } finally {
      setLoading(false);
    }
  }

  if (!post) return <div className="page">Loading…</div>;

  return (
    <div className="page">
      <div className="breadcrumbs">
        <Link to="/">Thinkers</Link>
        <span className="crumb-sep">›</span>
        <span>Post</span>
      </div>

      <h1 className="title">{post.title}</h1>

      <div className="split" role="region" aria-label="Article and analysis">
        {/* Left: Original content */}
        <div>
          <div className="h2">Article</div>
          <div className="rule" />
          <div className="article" dangerouslySetInnerHTML={{ __html: cleanHTML }} />
        </div>

        {/* Right: Interpretation */}
        <aside className="analysis" aria-label="Analysis">
          <div className="h2">Analysis</div>
          <div className="rule" />

          <div className="kv" aria-label="Key fields">
            <div className="k">Main claim</div>
            <div className="v">{post.analysis?.main_claim || "—"}</div>

            <div className="k">Bias</div>
            <div className="v">{post.analysis?.bias || "—"}</div>
          </div>

          <div className="h3">Ask the article</div>
          <div className="small mb12">
            One question at a time. Output is treated as model text (monospace).
          </div>

          <textarea
            className="input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What is the author assuming when they argue that…"
          />

          <div className="controls mt12">
            <button className="button" onClick={ask} disabled={loading}>
              {loading ? "Thinking…" : "Ask"}
            </button>
            <button
              className="linkButton"
              onClick={() => {
                setQuestion("");
                setAnswer(null);
                setAskErr(false);
              }}
              type="button"
            >
              Clear
            </button>
          </div>

          {askErr && <div className="meta mt12">Error contacting reasoning engine.</div>}

          {answer?.answer && (
            <div className="mt18">
              <div className="h3">Answer</div>
              <p className="m0" style={{ fontFamily: "var(--mono)", fontSize: "0.95rem" }}>
                {answer.answer}
              </p>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}