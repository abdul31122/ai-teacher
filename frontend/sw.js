// ====== Service Worker — অফলাইন ক্যাশ ======

const CACHE_NAME = 'ai-teacher-v1';
const BOOK_CACHE = 'ai-teacher-books';

// অ্যাপের ফাইল ক্যাশ করো
const APP_FILES = [
    '/',
    '/index.html',
    '/style.css',
    '/app.js',
    '/manifest.json',
];

// ইনস্টল — অ্যাপ ফাইল ক্যাশ
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(APP_FILES);
        })
    );
    self.skipWaiting();
});

// অ্যাক্টিভেট — পুরনো ক্যাশ মুছো
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(k => k !== CACHE_NAME && k !== BOOK_CACHE)
                    .map(k => caches.delete(k))
            );
        })
    );
    self.clients.claim();
});

// ফেচ — ক্যাশ ফার্স্ট, তারপর নেটওয়ার্ক
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);
    
    // API কল — সবসময় নেটওয়ার্ক
    if (url.pathname.startsWith('/api/')) {
        return event.respondWith(fetch(event.request));
    }
    
    // PDF ফাইল — ক্যাশ ফার্স্ট (অফলাইনে বই পড়া)
    if (url.pathname.endsWith('.pdf') || url.href.includes('supabase')) {
        event.respondWith(
            caches.open(BOOK_CACHE).then(cache => {
                return cache.match(event.request).then(cached => {
                    if (cached) return cached; // ক্যাশে আছে!
                    
                    return fetch(event.request).then(response => {
                        // নতুন PDF ক্যাশে রাখো
                        cache.put(event.request, response.clone());
                        return response;
                    });
                });
            })
        );
        return;
    }
    
    // অন্য ফাইল — ক্যাশ ফার্স্ট
    event.respondWith(
        caches.match(event.request).then(cached => {
            return cached || fetch(event.request).then(response => {
                // ক্যাশে রাখো
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, clone);
                    });
                }
                return response;
            });
        }).catch(() => {
            // অফলাইনে এবং ক্যাশে নেই
            return new Response(
                '<h2 style="text-align:center;padding:40px;font-family:sans-serif;">📵 ইন্টারনেট নেই<br><small>বই পড়া যাবে, কিন্তু AI Teacher এর জন্য ইন্টারনেট লাগবে।</small></h2>',
                { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
            );
        })
    );
});
