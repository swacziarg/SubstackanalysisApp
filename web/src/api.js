import axios from "axios";

export const api = axios.create({
  baseURL: "http://127.0.0.1:10000",
});
export const getAuthorProfile = (id) => api.get(`/authors/${id}/profile`);
export const compareAuthors = (a, b) =>
  api.get(`/compare?author_a=${a}&author_b=${b}`);
