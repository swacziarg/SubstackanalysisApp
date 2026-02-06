import { useEffect, useState } from "react";
import { api } from "../api";
import { Link, useParams } from "react-router-dom";

export default function Author() {
  const { id } = useParams();
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    api.get(`/authors/${id}/posts`).then((res) => setPosts(res.data));
  }, [id]);

  return (
    <div style={{ padding: 40, maxWidth: 900, margin: "auto" }}>
      <h1>Posts</h1>

      {posts.map((p) => (
        <div
          key={p.id}
          style={{
            border: "1px solid #ddd",
            padding: 18,
            marginBottom: 18,
            borderRadius: 8,
          }}
        >
          <Link to={`/posts/${p.id}`}>
            <h2 style={{ marginBottom: 6 }}>{p.title || "Untitled"}</h2>
          </Link>

          <Link to={`/authors/${id}/profile`}>
            View belief profile
          </Link>

          <div style={{ marginTop: 8, color: "#666" }}>
            Bias: {p.bias_score ?? "unknown"}
          </div>

          <p style={{ marginTop: 10 }}>
            {p.main_claim || p.summary || "No analysis yet."}
          </p>
        </div>
      ))}
    </div>
  );
}