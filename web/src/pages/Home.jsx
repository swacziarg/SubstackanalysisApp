import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="page">
      <h1 className="title">Readable Intelligence</h1>

      <p className="meta">
        A research notebook for understanding how people think.
      </p>

      <div className="rule" />

      <section>
        <h2 className="h2">Mission</h2>
        <p>
          Most writing is skimmed, reacted to, and forgotten.
          This system exists to slow that down.
        </p>
        <p>
          Articles are treated as arguments.
          Authors are treated as belief systems.
        </p>
        <p>
          The goal is comprehension, not engagement.
        </p>
      </section>

      <div className="rule" />

      <section>
        <h2 className="h2">Structure</h2>

        <table className="table">
          <thead>
            <tr>
              <th>Page</th>
              <th>Question answered</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><Link to="/authors">Thinkers</Link></td>
              <td>Who to read</td>
            </tr>
            <tr>
              <td>Author</td>
              <td>What they wrote</td>
            </tr>
            <tr>
              <td>Post</td>
              <td>What the article argues</td>
            </tr>
            <tr>
              <td>Profile</td>
              <td>What they believe</td>
            </tr>
          </tbody>
        </table>
      </section>

      <div className="rule" />

      <section>
        <h2 className="h2">How to use</h2>
        <ol>
          <li>Choose a thinker</li>
          <li>Scan their posts</li>
          <li>Read one article with analysis</li>
          <li>Open the worldview summary last</li>
        </ol>

        <p className="meta">
          Conclusions should follow evidence.
        </p>
      </section>

      <div className="rule" />

      <section>
        <h2 className="h2">Start</h2>
        <p>
          <Link to="/authors">Browse thinkers →</Link>
        </p>
      </section>
    </div>
  );
}