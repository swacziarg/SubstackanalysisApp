import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAuthorsCached } from "../api";
import { startBackgroundWarm } from "../preload";
export default function Authors() {
  const [authors, setAuthors] = useState([]);
    useEffect(() => {
    getAuthorsCached().then((a) => {
        setAuthors(a);
        startBackgroundWarm(); // ensures warm even if user lands deep link
    });
    }, []);

  return (
    <div style={{ padding: 40 }}>
      <h1>Authors</h1>

      {authors.map((a) => (
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
