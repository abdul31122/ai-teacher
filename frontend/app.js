// ====== AI Teacher App ======
const API_BASE = 'https://project-kq2nc.vercel.app';
const SUPABASE_URL = 'https://gbgkicmmmbobrsuaxldg.supabase.co';
const PDF_BASE = `${SUPABASE_URL}/storage/v1/object/public/books`;

// ====== State ======
let currentView = 'library';
let currentBook = null;
let pdfDoc = null;
let currentPage = 1;
let totalPages = 0;
let chatHistory = [];
let chatOpen = false;
let userId = '';
let rendering = false;

// ====== Init ======
document.addEventListener('DOMContentLoaded', () => {
    userId = getOrCreateUserId();
    checkBlockAndBroadcast();
    loadBooks();
});

// ====== User ID ======
function getOrCreateUserId() {
    let id = localStorage.getItem('ai_teacher_uid');
    if (!id) {
        id = 'u_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
        localStorage.setItem('ai_teacher_uid', id);
    }
    return id;
}

// ====== Block & Broadcast Check ======
async function checkBlockAndBroadcast() {
    try {
        const res = await fetch(`${API_BASE}/api/admin?action=check&user_id=${userId}`);
        const data = await res.json();
        if (data.blocked) {
            document.getElementById('blockedScreen').classList.remove('hidden');
            return;
        }
        if (data.broadcast && data.broadcast.message) {
            document.getElementById('broadcastText').textContent = data.broadcast.message;
            document.getElementById('broadcastBanner').classList.remove('hidden');
        }
    } catch (e) { /* ignore */ }
}

function dismissBroadcast() {
    document.getElementById('broadcastBanner').classList.add('hidden');
}

// ====== Load Books ======
async function loadBooks() {
    const grid = document.getElementById('bookGrid');
    try {
        const res = await fetch(`${API_BASE}/api/books`);
        const data = await res.json();
        grid.innerHTML = data.books.map(book => `
            <div class="book-card" onclick="openBook('${book.id}')">
                <div class="book-cover">${book.cover}</div>
                <div class="book-title">${book.title}</div>
                <div class="book-info">${book.code} • ${book.pages} pages</div>
                <div class="book-badge">SSC</div>
            </div>
        `).join('');
    } catch (e) {
        grid.innerHTML = `
            <div class="book-card" onclick="openBook('bangla-2nd-paper')">
                <div class="book-cover">📕</div>
                <div class="book-title">বাংলা দ্বিতীয় পত্র (ব্যাকরণ)</div>
                <div class="book-info">SSC-2651 • 301 pages</div>
                <div class="book-badge">SSC</div>
            </div>
        `;
    }
}

function filterBooks() {
    const q = document.getElementById('searchInput').value.toLowerCase();
    document.querySelectorAll('.book-card').forEach(c => {
        const t = c.querySelector('.book-title').textContent.toLowerCase();
        c.style.display = t.includes(q) ? '' : 'none';
    });
}

// ====== Open Book ======
async function openBook(bookId) {
    currentBook = bookId;
    showView('reader');
    document.getElementById('readerLoading').style.display = 'flex';

    const pdfUrl = `${PDF_BASE}/${bookId}.pdf`;

    try {
        const loadingTask = pdfjsLib.getDocument({
            url: pdfUrl,
            cMapUrl: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/cmaps/',
            cMapPacked: true,
        });

        pdfDoc = await loadingTask.promise;
        totalPages = pdfDoc.numPages;
        currentPage = 1;

        document.getElementById('readerLoading').style.display = 'none';
        await renderPage(currentPage);
        cacheBook(pdfUrl);
    } catch (e) {
        document.getElementById('readerLoading').innerHTML = `
            <span style="font-size:3rem">📚</span>
            <p style="margin-top:16px;color:#666">Could not load book.</p>
            <p style="font-size:0.8rem;color:#999;margin-top:8px">Check your internet connection.</p>
            <button onclick="openBook('${bookId}')" style="margin-top:16px;padding:10px 24px;background:#1a7f5a;color:white;border:none;border-radius:10px;cursor:pointer">Retry</button>
        `;
    }
}

// ====== Render Page ======
async function renderPage(num) {
    if (!pdfDoc || rendering) return;
    rendering = true;

    try {
        const page = await pdfDoc.getPage(num);
        const canvas = document.getElementById('pdfCanvas');
        const ctx = canvas.getContext('2d');

        const containerWidth = document.getElementById('pdfContainer').clientWidth;
        const viewport = page.getViewport({ scale: 1 });
        const scale = Math.min((containerWidth - 8) / viewport.width, 2.0);
        const scaledViewport = page.getViewport({ scale });

        canvas.width = scaledViewport.width;
        canvas.height = scaledViewport.height;

        await page.render({ canvasContext: ctx, viewport: scaledViewport }).promise;
        document.getElementById('pageInfo').textContent = `${num} / ${totalPages}`;

        // Scroll to top on page change
        document.getElementById('pdfContainer').scrollTop = 0;
    } catch (e) {
        console.error('Render error:', e);
    }

    rendering = false;
}

// ====== Page Navigation ======
function prevPage() {
    if (currentPage > 1) { currentPage--; renderPage(currentPage); }
}
function nextPage() {
    if (currentPage < totalPages) { currentPage++; renderPage(currentPage); }
}

// ====== Swipe Gesture ======
let touchStartX = 0, touchStartY = 0;

document.addEventListener('touchstart', e => {
    if (currentView !== 'reader') return;
    touchStartX = e.changedTouches[0].screenX;
    touchStartY = e.changedTouches[0].screenY;
}, { passive: true });

document.addEventListener('touchend', e => {
    if (currentView !== 'reader') return;
    const dx = touchStartX - e.changedTouches[0].screenX;
    const dy = Math.abs(touchStartY - e.changedTouches[0].screenY);
    if (Math.abs(dx) > 60 && dy < 100) {
        if (dx > 0) nextPage();
        else prevPage();
    }
}, { passive: true });

// ====== Keyboard ======
document.addEventListener('keydown', e => {
    if (currentView === 'reader') {
        if (e.key === 'ArrowLeft') prevPage();
        if (e.key === 'ArrowRight') nextPage();
    }
});

// ====== View Management ======
function showView(view) {
    currentView = view;
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

    if (view === 'reader') {
        document.getElementById('readerView').classList.add('active');
        document.getElementById('backBtn').classList.remove('hidden');
        document.getElementById('headerTitle').textContent = '📖 Reading';
    } else {
        document.getElementById('libraryView').classList.add('active');
        document.getElementById('backBtn').classList.add('hidden');
        document.getElementById('headerTitle').textContent = '📚 AI Teacher';
    }
}

function goBack() {
    showView('library');
    pdfDoc = null;
}

// ====== Chat ======
function toggleChat() {
    chatOpen = !chatOpen;
    document.getElementById('chatPanel').classList.toggle('open', chatOpen);
    if (chatOpen) document.getElementById('userInput').focus();
}

async function sendMessage() {
    const input = document.getElementById('userInput');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    addMessage(text, 'user');
    chatHistory.push({ role: 'user', content: text });

    const loadingId = addMessage('⏳ Thinking...', 'loading');

    try {
        const res = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: chatHistory.slice(-10),
                book_context: currentBook ? `Book: ${currentBook}, Page: ${currentPage}/${totalPages}` : ''
            })
        });
        const data = await res.json();
        removeMessage(loadingId);

        if (data.reply) {
            addMessage(data.reply, 'ai');
            chatHistory.push({ role: 'assistant', content: data.reply });
        } else if (data.error) {
            addMessage('❌ Error: ' + data.error, 'ai');
        }
    } catch (e) {
        removeMessage(loadingId);
        addMessage('📵 No internet. You can still read books offline!', 'ai');
    }
}

function addMessage(text, type) {
    const container = document.getElementById('chatMessages');
    const div = document.createElement('div');
    const id = 'msg-' + Date.now();
    div.id = id;
    div.className = `msg ${type}`;
    div.innerHTML = text.replace(/\n/g, '<br>');
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function quickAction(action) {
    const ctx = currentPage ? ` (Page ${currentPage})` : '';
    document.getElementById('userInput').value = action + ctx;
    if (!chatOpen) toggleChat();
    setTimeout(() => sendMessage(), 100);
}

// ====== Offline Cache ======
async function cacheBook(url) {
    if ('caches' in window) {
        try {
            const cache = await caches.open('ai-teacher-books');
            await cache.add(url);
        } catch (e) { /* ignore */ }
    }
}
