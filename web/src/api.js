//src/api.js
import axios from "axios";
import { cache } from "./store/cache";
import { fetchOnce } from "./store/fetchOnce";
export const api = axios.create({
  baseURL: "http://127.0.0.1:10000",
});
export const getAuthorProfile = (id) => api.get(`/authors/${id}/profile`);
export const compareAuthors = (a, b) =>
  api.get(`/compare?author_a=${a}&author_b=${b}`);
export function getAuthorsCached() {
  return fetchOnce("authors", async () => {
    const res = await api.get("/authors");
    return res.data;
  });
}

export function getPostsCached(authorId) {
  return fetchOnce(`posts:${authorId}`, async () => {
    const res = await api.get(`/authors/${authorId}/posts`);
    return res.data;
  });
}
export function getPostCached(postId) {
  return fetchOnce(`post:${postId}`, async () => {
    const res = await api.get(`/posts/${postId}`);
    return res.data;
  });
}
export function getProfileCached(authorId) {
  return fetchOnce(`profile:${authorId}`, async () => {
    const res = await api.get(`/authors/${authorId}/profile`);
    return res.data;
  });
}
