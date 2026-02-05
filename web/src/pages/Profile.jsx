import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";

export default function Profile() {
  const { authorId } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get(`/authors/${authorId}/profile`)
      .then(res => setData(res.data))
      .catch(() => setData({ error: true }));
  }, [authorId]);

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
          {data.beliefs?.length
            ? data.beliefs.map((b, i) => <li key={i}>{b}</li>)
            : <li>No recurring claims detected yet.</li>}
        </ul>
      </section>

      <section>
        <h2>Recurring Topics</h2>
        <ul>
          {data.recurring_topics?.length
            ? data.recurring_topics.map((t, i) => <li key={i}>{t}</li>)
            : <li>No dominant topics yet.</li>}
        </ul>
      </section>

      <section>
        <h2>Bias Overview</h2>
        <pre>{JSON.stringify(data.bias_overview, null, 2)}</pre>
      </section>
    </div>
  );
}