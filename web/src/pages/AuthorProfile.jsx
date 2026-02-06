import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getProfileCached } from "../api";

export default function AuthorProfile() {
  const { id } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    getProfileCached(id).then(setData);
  }, [id]);

  if (!data) return <div>Loading...</div>;

  return (
    <div style={{ maxWidth: 900, margin: "auto" }}>
      <h1>Author Beliefs</h1>

      <h2>Summary</h2>
      <p>{data.summary}</p>

      <h2>Core Beliefs</h2>
      <ul>
        {data.beliefs?.map((b, i) => (
          <li key={i}>{b}</li>
        ))}
      </ul>

      <h2>Recurring Topics</h2>
      <ul>
        {data.recurring_topics?.map((t, i) => (
          <li key={i}>{t}</li>
        ))}
      </ul>

      <h2>Bias Overview</h2>
      <pre>{JSON.stringify(data.bias_overview, null, 2)}</pre>
    </div>
  );
}
