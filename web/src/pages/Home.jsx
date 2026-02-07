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
          There is considerable overlap between what people read and what they already know.
        </p>
        <p>
          This project aims to break that feedback loop by surfacing the beliefs and biases of writers, based on what they actually write.
        </p>
        <p>
          The main goal is to help readers find thinkers with different perspectives, and to understand those perspectives in a structured way. 
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
              <td><Link to="/authors">Authors list</Link></td>
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
          <li>Read articles</li>
          <li>Open the worldview summary</li>
        </ol>

        <p className="meta">
          Conclusions should follow evidence.
        </p>
      </section>

      <div className="rule" />

      <section>
        <h2 className="h2">Start</h2>
        <p>
          <Link to="/authors">Browse authors →</Link>
        </p>
      </section>
    </div>
  );
}