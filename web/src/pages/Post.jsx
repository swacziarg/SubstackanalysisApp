import { useEffect, useState } from "react";
import { api } from "../api";
import { useParams } from "react-router-dom";
import DOMPurify from "dompurify";
import "../article.css";

export default function Post() {
  const { id } = useParams();

  const [post, setPost] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get(`/posts/${id}`).then((res) => setPost(res.data));
  }, [id]);

  async function ask() {
    setLoading(true);
    const res = await api.post(
    `/posts/${id}/ask`,
    { question }   // JSON body
    );
    setAnswer(res.data);
    setLoading(false);
  }

  if (!post) return <div style={{ padding: 40 }}>Loading...</div>;

  const cleanHTML = DOMPurify.sanitize(post.html || "");

  return (
    <div style={{ display: "flex", gap: 40, padding: 40 }}>
      {/* Article */}
      <div style={{ width: "60%" }}>
        <h1>{post.title || "Untitled"}</h1>

        <div
          className="article"
          dangerouslySetInnerHTML={{ __html: cleanHTML }}
        />
      </div>

      {/* AI Panel */}
      <div style={{ width: "40%" }}>
        <h2>AI Analysis</h2>
        <p><b>Main claim:</b> {post.analysis?.main_claim}</p>
        <p><b>Bias:</b> {post.analysis?.bias}</p>

        <hr />

        <h2>Ask the article</h2>

        <input
          style={{ width: "100%", padding: 8 }}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What does the author believe?"
        />

        <button onClick={ask} disabled={loading}>
          {loading ? "Thinking..." : "Ask"}
        </button>

        {answer && (
          <div style={{ marginTop: 20 }}>
            <h3>Answer</h3>
            <p>{answer.answer}</p>
          </div>
        )}
      </div>
    </div>
  );
}