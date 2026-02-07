// src/pages/Author.jsx
import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getPostsCached } from "../api";

export default function Author() {
  const { id } = useParams();
  const [posts, setPosts] = useState([]);
  const [err, setErr] = useState(false);

  useEffect(() => {
    setErr(false);
    getPostsCached(id)
      .then(setPosts)
      .catch(() => setErr(true));
  }, [id]);

  const rows = useMemo(() => {
    return (posts || []).map((p) => ({
      id: p.id,
      title: p.title || "Untitled",
      bias: p.bias_score ?? p.analysis?.bias ?? "unknown",
      claim: p.main_claim || p.summary || "No analysis yet.",
    }));
  }, [posts]);

  return (
    <div className="page">
      <div className="breadcrumbs">
        <Link to="/authors">Authors list</Link>
        <span className="crumb-sep">›</span>
        <span>Author</span>
      </div>

      <h1 className="title">Posts</h1>

      <div className="meta">
        <Link to={`/authors/${id}/profile`}>Worldview summary →</Link>
      </div>
      <div className="meta">
        <Link to={`/authors/${id}/dialogue`}>Dialogue →</Link>
      </div>

      <div className="rule" />

      {err && <div className="meta">Failed to load posts.</div>}
      {!err && posts.length === 0 && <div className="meta">Loading…</div>}

      {rows.length > 0 && (
        <table className="table" aria-label="Posts">
          <thead>
            <tr>
              <th style={{ width: "52ch" }}>Title</th>
              <th style={{ width: "14ch" }}>Bias</th>
              <th>Main claim</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id}>
                <td>
                  <Link to={`/authors/${id}/posts/${p.id}`}>{p.title}</Link>
                </td>
                <td className="small">{String(p.bias)}</td>
                <td className="small">{p.claim}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}