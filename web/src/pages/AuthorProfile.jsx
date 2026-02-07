// src/pages/AuthorProfile.jsx
import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getProfileCached } from "../api";

export default function AuthorProfile() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    setErr(false);
    getProfileCached(id)
      .then(setData)
      .catch(() => setErr(true));
  }, [id]);

  const beliefs = useMemo(() => data?.beliefs || [], [data]);
  const topics = useMemo(() => data?.recurring_topics || [], [data]);

  if (err) return <div className="page">Failed to load profile.</div>;
  if (!data) return <div className="page">Loading worldview…</div>;

  return (
    <div className="page">
      <div className="breadcrumbs">
        <Link to="/authors">Authors list</Link>
        <span className="crumb-sep">›</span>
        <Link to={`/authors/${id}`}>Author</Link>
        <span className="crumb-sep">›</span>
        <span>Profile</span>
      </div>

      <h1 className="title">Worldview</h1>
      <div className="meta readable">
        Structured as a research summary: claims, recurring themes, and bias tendencies.
      </div>

      <div className="rule" />

      <section className="readable" aria-label="Summary">
        <h2 className="h2">Summary</h2>
        <p className="m0">{data.summary || "Not enough data yet."}</p>
      </section>

      <div className="rule" />

      <section className="readable" aria-label="Core beliefs">
        <h2 className="h2">Core beliefs</h2>
        {beliefs.length === 0 ? (
          <div className="meta">No recurring claims detected yet.</div>
        ) : (
          <ul>
            {beliefs.map((b, i) => (
              <li key={i}>{b}</li>
            ))}
          </ul>
        )}
      </section>

      <div className="rule" />

      <section className="readable" aria-label="Recurring topics">
        <h2 className="h2">Recurring topics</h2>
        {topics.length === 0 ? (
          <div className="meta">No dominant topics yet.</div>
        ) : (
          <ul>
            {topics.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
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
  );
}