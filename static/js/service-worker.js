const CACHE_NAME = 'yara-cache-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/css/index.css',
  '/static/img/pwa-icon.svg'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(resp => resp || fetch(event.request).then(response => {
      return caches.open(CACHE_NAME).then(cache => {
        try { cache.put(event.request, response.clone()); } catch(e){}
        return response;
      });
    }).catch(()=>caches.match('/static/img/pwa-icon.svg')))
  );
});
