import { useEffect, useState } from "react";
import { api } from "../api";
import { Link } from "react-router-dom";

export default function Authors() {
  const [authors, setAuthors] = useState([]);

  useEffect(() => {
    api.get("/authors").then(res => setAuthors(res.data));
  }, []);

  return (
    <div style={{ padding: 40 }}>
      <h1>Authors</h1>

      {authors.map(a => (
        <div key={a.id} style={{ marginBottom: 12 }}>
          <Link to={`/authors/${a.id}`}>
            <b>{a.name}</b>
          </Link>
        </div>
      ))}
      <Link to="/compare">Compare thinkers</Link>
    </div>
  );
}