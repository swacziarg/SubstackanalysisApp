import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home.jsx";
import Authors from "./pages/Authors.jsx";
import Author from "./pages/Author.jsx";
import Post from "./pages/Post.jsx";
import Compare from "./pages/Compare.jsx";
import AuthorProfile from "./pages/AuthorProfile.jsx";
import Nav from "./components/Nav.jsx";
import { startBackgroundWarm } from "./preload";
import "./ui.css";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter future={{ v7_startTransition: true }}>
      <div className="app">
        <Nav />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/authors" element={<Authors />} />
          <Route path="/authors/:id" element={<Author />} />
          <Route path="/authors/:id/profile" element={<AuthorProfile />} />
          <Route path="/posts/:id" element={<Post />} />
          <Route path="/compare" element={<Compare />} />
        </Routes>
      </div>
    </BrowserRouter>
  </React.StrictMode>
);

startBackgroundWarm();