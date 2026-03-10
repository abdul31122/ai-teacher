// ====== AI Teacher — মূল অ্যাপ ======

// API বেস URL (Vercel ডিপ্লয়ের পর আপডেট হবে)
const API_BASE = window.location.origin;

// ====== স্টেট ======
let currentView = 'library';
let currentBook = null;
let pdfDoc = null;
let currentPage = 1;
let totalPages = 0;
let chatHistory = [];
let chatOpen = false;

// ====== বই লোড ======
async function loadBooks() {
    const grid = document.getElementById('bookGrid');
    
    try {
        const res = await fetch(`${API_BASE}/api/books`);
        const data = await res.json();
        
        grid.innerHTML = data.books.map(book => `
            <div class="book-card" onclick="openBook('${book.id}')">
                <div class="book-cover">${book.cover}</div>
                <div class="book-title">${book.title}</div>
                <div class="book-info">${book.code} • ${book.pages} পাতা</div>
            </div>
        `).join('');
    } catch (e) {
        // API না পেলে ডিফল্ট বই দেখাও
        grid.innerHTML = `
            <div class="book-card" onclick="openBook('bangla-2nd-paper')">
                <div class="book-cover">📕</div>
                <div class="book-title">বাংলা দ্বিতীয় পত্র (ব্যাকরণ)</div>
                <div class="book-info">SSC-2651 • ৩০১ পাতা</div>
            </div>
        `;
    }
}

// ====== বই সার্চ ======
function filterBooks() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    const cards = document.querySelectorAll('.book-card');
    cards.forEach(card => {
        const title = card.querySelector('.book-title').textContent.toLowerCase();
        card.style.display = title.includes(query) ? '' : 'none';
    });
}

// ====== বই ওপেন ======
async function openBook(bookId) {
    currentBook = bookId;
    showView('reader');
    
    // PDF URL — Supabase থেকে লোড হবে
    // এখন ডেমোর জন্য placeholder
    const pdfUrl = getPdfUrl(bookId);
    
    if (pdfUrl) {
        try {
            const loadingTask = pdfjsLib.getDocument(pdfUrl);
            pdfDoc = await loadingTask.promise;
            totalPages = pdfDoc.numPages;
            currentPage = 1;
            renderPage(currentPage);
            
            // ক্যাশে সেভ
            cacheBook(bookId, pdfUrl);
        } catch (e) {
            document.getElementById('pdfContainer').innerHTML = `
                <div style="padding: 40px; text-align: center; color: #666;">
                    <p style="font-size: 3rem;">📚</p>
                    <p style="margin-top: 16px;">বই লোড হচ্ছে না।</p>
                    <p style="font-size: 0.85rem; margin-top: 8px;">PDF ফাইল Supabase-এ আপলোড করুন।</p>
                </div>
            `;
        }
    }
}

// ====== PDF URL ======
function getPdfUrl(bookId) {
    return `https://gbgkicmmmbobrsuaxldg.supabase.co/storage/v1/object/public/books/${bookId}.pdf`;
}

// ====== পাতা রেন্ডার ======
async function renderPage(num) {
    if (!pdfDoc) return;
    
    const page = await pdfDoc.getPage(num);
    const canvas = document.getElementById('pdfCanvas');
    const ctx = canvas.getContext('2d');
    
    // মোবাইলে ফিট করার জন্য স্কেল
    const containerWidth = document.getElementById('pdfContainer').clientWidth;
    const viewport = page.getViewport({ scale: 1 });
    const scale = (containerWidth - 16) / viewport.width;
    const scaledViewport = page.getViewport({ scale });
    
    canvas.width = scaledViewport.width;
    canvas.height = scaledViewport.height;
    
    await page.render({
        canvasContext: ctx,
        viewport: scaledViewport
    }).promise;
    
    // পাতা নম্বর আপডেট
    document.getElementById('pageInfo').textContent = `${num}/${totalPages}`;
}

// ====== পাতা উল্টানো ======
function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        renderPage(currentPage);
    }
}

function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        renderPage(currentPage);
    }
}

// ====== সোয়াইপ জেসচার ======
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', e => {
    if (currentView !== 'reader') return;
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', e => {
    if (currentView !== 'reader') return;
    touchEndX = e.changedTouches[0].screenX;
    const diff = touchStartX - touchEndX;
    
    if (Math.abs(diff) > 50) {
        if (diff > 0) nextPage();  // বামে সোয়াইপ → পরের পাতা
        else prevPage();           // ডানে সোয়াইপ → আগের পাতা
    }
});

// ====== ভিউ ম্যানেজমেন্ট ======
function showView(view) {
    currentView = view;
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(view === 'library' ? 'libraryView' : 'readerView').classList.add('active');
    
    const backBtn = document.getElementById('backBtn');
    const title = document.getElementById('headerTitle');
    
    if (view === 'reader') {
        backBtn.classList.remove('hidden');
        title.textContent = '📖 বই পড়ুন';
    } else {
        backBtn.classList.add('hidden');
        title.textContent = '📚 AI Teacher';
    }
}

function goBack() {
    showView('library');
    pdfDoc = null;
}

// ====== চ্যাটবট ======
function toggleChat() {
    chatOpen = !chatOpen;
    document.getElementById('chatPanel').classList.toggle('open', chatOpen);
    if (chatOpen) {
        document.getElementById('userInput').focus();
    }
}

async function sendMessage() {
    const input = document.getElementById('userInput');
    const text = input.value.trim();
    if (!text) return;
    
    input.value = '';
    addMessage(text, 'user');
    
    // চ্যাট হিস্টোরিতে যোগ
    chatHistory.push({ role: 'user', content: text });
    
    // লোডিং দেখাও
    const loadingId = addMessage('⏳ চিন্তা করছি...', 'loading');
    
    try {
        const res = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: chatHistory.slice(-10), // শেষ ১০টা মেসেজ
                book_context: currentBook ? `বর্তমান বই: ${currentBook}, পাতা: ${currentPage}` : ''
            })
        });
        
        const data = await res.json();
        removeMessage(loadingId);
        
        if (data.reply) {
            addMessage(data.reply, 'ai');
            chatHistory.push({ role: 'assistant', content: data.reply });
        } else {
            addMessage('❌ দুঃখিত, একটু সমস্যা হয়েছে। আবার চেষ্টা করুন।', 'ai');
        }
    } catch (e) {
        removeMessage(loadingId);
        addMessage('❌ সার্ভারে কানেক্ট হচ্ছে না। ইন্টারনেট চেক করুন।', 'ai');
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

// ====== কুইক অ্যাকশন ======
function quickAction(action) {
    const pageContext = currentPage ? ` (পাতা ${currentPage})` : '';
    document.getElementById('userInput').value = action + pageContext;
    
    if (!chatOpen) toggleChat();
    sendMessage();
}

// ====== অফলাইন ক্যাশ ======
async function cacheBook(bookId, url) {
    if ('caches' in window) {
        try {
            const cache = await caches.open('ai-teacher-books');
            await cache.add(url);
            console.log(`✅ বই ক্যাশ হয়েছে: ${bookId}`);
        } catch (e) {
            console.log('ক্যাশ ব্যর্থ:', e);
        }
    }
}

// ====== কীবোর্ড শর্টকাট ======
document.addEventListener('keydown', e => {
    if (currentView === 'reader') {
        if (e.key === 'ArrowLeft') prevPage();
        if (e.key === 'ArrowRight') nextPage();
    }
});

// ====== অ্যাপ শুরু ======
document.addEventListener('DOMContentLoaded', () => {
    loadBooks();
});
