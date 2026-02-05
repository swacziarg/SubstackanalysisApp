import { useEffect, useState } from "react";
import { api } from "../api";
import { Link, useParams } from "react-router-dom";

export default function Author() {
  const { id } = useParams();
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    api.get(`/authors/${id}/posts`).then(res => setPosts(res.data));
  }, [id]);

  return (
    <div style={{ padding: 40 }}>
      <h1>Posts</h1>

      {posts.map(p => (
        <div key={p.id} style={{
          border: "1px solid #ddd",
          padding: 16,
          marginBottom: 16
        }}>
          <Link to={`/post/${p.id}`}>
            <h3>{p.title}</h3>
          </Link>
          <Link to={`/authors/${id}/profile`}>View belief profile</Link>
          <div>Bias: {p.bias ?? "unknown"}</div>
          <div>{p.summary}</div>
        </div>
      ))}
    </div>
  );
}