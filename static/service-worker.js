const CACHE_NAME = 'icm-bf-cache-v1';
const ASSETS = [
  '/',
  '/static/style.css',
  '/static/script.js'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then(resp => {
      return resp || fetch(event.request).then(res => {
        return caches.open(CACHE_NAME).then(cache => {
          try { cache.put(event.request, res.clone()); } catch (e) {}
          return res;
        });
      });
    }).catch(()=>caches.match('/'))
  );
});
