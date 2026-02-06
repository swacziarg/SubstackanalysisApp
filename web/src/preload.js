import {
  getAuthorsCached,
  getPostsCached,
  getProfileCached,
  getPostCached,
} from "./api";

export async function startBackgroundWarm() {
  // ---------- Phase 1: critical (home page) ----------
  const authors = await getAuthorsCached();

  // ---------- Phase 2: medium (navigation) ----------
  const postsByAuthor = await Promise.all(
    authors.map(async (a) => ({
      author: a,
      posts: await getPostsCached(a.id),
    })),
  );

  // profiles can load in parallel
  authors.forEach((a) => getProfileCached(a.id));

  // ---------- Phase 3: deep (documents) ----------
  deepWarmPosts(postsByAuthor);
}

function deepWarmPosts(postsByAuthor) {
  const queue = postsByAuthor.flatMap((x) => x.posts.map((p) => p.id));
  let i = 0;

  async function worker() {
    while (i < queue.length) {
      const id = queue[i++];
      try {
        await getPostCached(id);
      } catch {}
      await sleep(60); // prevents backend hammering
    }
  }

  for (let k = 0; k < 4; k++) worker();
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}
