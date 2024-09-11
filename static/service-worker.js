
const CACHE_NAME = 'offline-cache';
const OFFLINE_URL = "/network_error/";

console.log("Service Worker is running");

const OFFLINE_ASSETS = [
    OFFLINE_URL,
    "/shop",
    "/static/service-worker.js",
    // Add other assets you want to cache, like CSS, images, etc.
];

self.addEventListener('install', event => {
  this.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Cache opened:', cache);
                console.log('Adding assets to cache:', OFFLINE_ASSETS);
                return cache.addAll(OFFLINE_ASSETS);
            })
            .catch(error => {
                console.error('Failed to cache offline assets:', error);
            })
    );
  
});

self.addEventListener('activate', event => {
    console.log("Service worker is activated");
    
    // removes old caches
    event.waitUntil(
      caches.keys().then((cacheNames) => {
          return Promise.all(
              cacheNames.map((cacheName) => {
                  if (cacheName !== CACHE_NAME) {
                    console.log('Service Worker: Fetching');
                      return caches.delete(cacheName);
                  }
              })
          );
      })
  );
  return self.clients.claim();

});


self.addEventListener('fetch', function(event){
  console.log('Service Worker: Fetching');

  event.respondWith(
    fetch(event.request).catch(() => {
        return caches.match(OFFLINE_URL);
    })
);
});

