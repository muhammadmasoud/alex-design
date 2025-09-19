// Service Worker for aggressive image caching
const CACHE_NAME = 'portfolio-images-v1';
const IMAGE_CACHE_DURATION = 30 * 24 * 60 * 60 * 1000; // 30 days in milliseconds

self.addEventListener('install', (event) => {
  console.log('Image cache service worker installed');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('Image cache service worker activated');
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Only handle image requests
  if (event.request.url.includes('/media/') && 
      /\.(jpg|jpeg|png|gif|webp|bmp|tiff)$/i.test(event.request.url)) {
    
    event.respondWith(
      caches.open(CACHE_NAME).then(cache => {
        return cache.match(event.request).then(cachedResponse => {
          if (cachedResponse) {
            // Check if cache is still fresh
            const cacheDate = new Date(cachedResponse.headers.get('date'));
            const now = new Date();
            if (now - cacheDate < IMAGE_CACHE_DURATION) {
              return cachedResponse;
            }
          }
          
          // Fetch new image and cache it
          return fetch(event.request).then(response => {
            // Only cache successful responses
            if (response.status === 200) {
              cache.put(event.request, response.clone());
            }
            return response;
          }).catch(() => {
            // Return cached version if network fails
            return cachedResponse || new Response('Image not available', { status: 404 });
          });
        });
      })
    );
  }
});
