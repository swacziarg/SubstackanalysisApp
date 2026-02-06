import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Authors from "./pages/Authors.jsx";
import Author from "./pages/Author.jsx";
import Post from "./pages/Post.jsx";
import Compare from "./pages/Compare.jsx";
import AuthorProfile from "./pages/AuthorProfile.jsx";
import Profile from "./pages/Profile.jsx";
import { startBackgroundWarm } from "./preload";

ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter future={{ v7_startTransition: true }}>
    <Routes>
      <Route path="/" element={<Authors />} />
      <Route path="/authors/:id" element={<Author />} />
      <Route path="/authors/:id/profile" element={<AuthorProfile />} />
      <Route path="/posts/:id" element={<Post />} />
      <Route path="/compare" element={<Compare />} />
    </Routes>
  </BrowserRouter>,
);

// start warming AFTER UI exists
startBackgroundWarm();
