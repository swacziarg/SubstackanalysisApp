//src/store/fetchOnce.js
const store = new Map();

export function peek(key) {
  return store.get(key)?.data ?? null;
}

export async function fetchOnce(key, fetcher) {
  const existing = store.get(key);

  // already resolved
  if (existing?.data !== undefined) return existing.data;

  // in flight
  if (existing?.promise) return existing.promise;

  // start request
  const promise = fetcher().then((res) => {
    store.set(key, { data: res });
    return res;
  });

  store.set(key, { promise });
  return promise;
}
