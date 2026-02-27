const CACHE = 'dropscan-v2';
const STATIC = ['/static/favicon.svg', '/static/manifest.json'];

self.addEventListener('install', function(e) {
    e.waitUntil(caches.open(CACHE).then(function(c) { return c.addAll(STATIC); }));
    self.skipWaiting();
});

self.addEventListener('activate', function(e) {
    e.waitUntil(
        caches.keys().then(function(keys) {
            return Promise.all(keys.filter(function(k) { return k !== CACHE; }).map(function(k) { return caches.delete(k); }));
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', function(e) {
    var req = e.request;
    if (req.method !== 'GET') return;

    // API calls: network-first, no cache
    if (req.url.includes('/api/')) {
        e.respondWith(fetch(req).catch(function() { return new Response('{"error":"offline"}', {headers:{'Content-Type':'application/json'}}); }));
        return;
    }

    // Static assets: cache-first
    if (req.url.includes('/static/')) {
        e.respondWith(
            caches.match(req).then(function(cached) {
                if (cached) return cached;
                return fetch(req).then(function(res) {
                    var clone = res.clone();
                    caches.open(CACHE).then(function(c) { c.put(req, clone); });
                    return res;
                });
            })
        );
        return;
    }

    // HTML pages: network-first, fall back to cache
    e.respondWith(
        fetch(req).then(function(res) {
            var clone = res.clone();
            caches.open(CACHE).then(function(c) { c.put(req, clone); });
            return res;
        }).catch(function() {
            return caches.match(req).then(function(cached) { return cached || caches.match('/'); });
        })
    );
});
