import { Link, useLocation } from "react-router-dom";
import "../ui.css";

export default function Nav() {
  const loc = useLocation();

  return (
    <div className="nav" role="navigation" aria-label="Primary">
      <div className="nav-inner">
        <Link className="brand" to="/">Readable Intelligence</Link>
        <span className="sep">·</span>
        <Link to="/authors" aria-current={loc.pathname.startsWith("/authors") ? "page" : undefined}>
          Thinkers
        </Link>
        <Link to="/compare" aria-current={loc.pathname.startsWith("/compare") ? "page" : undefined}>
          Compare
        </Link>
      </div>
    </div>
  );
}