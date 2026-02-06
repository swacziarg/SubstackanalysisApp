// store/cache.js
export const cache = {
  authors: null,

  postsByAuthor: new Map(),
  posts: new Map(),
  profiles: new Map(),

  inflight: new Map(),
};
