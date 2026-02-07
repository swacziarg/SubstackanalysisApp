// src/pages/Authors.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAuthorsCached } from "../api";
import { startBackgroundWarm } from "../preload";

export default function Authors() {
  const [authors, setAuthors] = useState([]);
  const [err, setErr] = useState(false);

  useEffect(() => {
    getAuthorsCached()
      .then((a) => {
        setAuthors(a);
        startBackgroundWarm();
      })
      .catch(() => setErr(true));
  }, []);

  return (
    <div className="page">

      <h1 className="title">Authors list</h1>

      <div className="rule" />

      {err && <div className="meta">Failed to load authors.</div>}

      {!err && authors.length === 0 && <div className="meta">Loading…</div>}

      {authors.length > 0 && (
        <table className="table" aria-label="Authors">
          <thead>
            <tr>
              <th style={{ width: "34ch" }}>Author</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {authors.map((a) => (
              <tr key={a.id}>
                <td>
                  <Link to={`/authors/${a.id}`}>{a.name}</Link>
                </td>
                <td className="small">{a.subdomain}.substack.com</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}