# 📚 AI Teacher — আপনার পড়ালেখার সহকারী

বাংলাদেশ উন্মুক্ত বিশ্ববিদ্যালয়ের SSC প্রোগ্রামের ছাত্রদের জন্য AI-ভিত্তিক টিউটর।

## ✨ ফিচারস

- 📖 **বই পড়া** — PDF হুবহু দেখায়, সোয়াইপে পাতা উল্টানো, পিঞ্চ জুম
- 🤖 **AI চ্যাটবট** — পাঠ বুঝিয়ে দেয়, MCQ বানায়, স্কোরিং করে
- 📵 **অফলাইন** — একবার বই লোড হলে ইন্টারনেট ছাড়াও পড়া যায়
- 📱 **মোবাইল ফ্রেন্ডলি** — ফোনে সুন্দর দেখায়

## 🚀 সেটআপ

### ১. অ্যাকাউন্ট বানান (ফ্রি)
- [Groq](https://console.groq.com) → API Key
- [GitHub](https://github.com) → Sign Up
- [Vercel](https://vercel.com) → Sign Up (GitHub দিয়ে)
- [Supabase](https://supabase.com) → Sign Up (GitHub দিয়ে)

### ২. Supabase সেটআপ
1. New Project বানান
2. Storage → New Bucket → নাম: `books` → Public করুন
3. `books` বাকেটে PDF আপলোড করুন
4. Settings → API → URL ও anon key কপি করুন

### ৩. Vercel-এ ডিপ্লয়
1. GitHub-এ এই রেপো পুশ করুন
2. Vercel → New Project → GitHub রেপো সিলেক্ট
3. Environment Variables এ যোগ করুন:
   - `GROQ_API_KEY` = আপনার Groq key
   - `SUPABASE_URL` = আপনার Supabase URL
   - `SUPABASE_KEY` = আপনার Supabase anon key
4. Deploy!

## 📁 স্ট্রাকচার

```
ai-teacher/
├── api/
│   ├── chat.py        ← AI চ্যাটবট API
│   └── books.py       ← বই তালিকা API
├── frontend/
│   ├── index.html     ← ওয়েবসাইট
│   ├── style.css      ← ডিজাইন
│   ├── app.js         ← ফিচার
│   ├── sw.js          ← অফলাইন ক্যাশ
│   └── manifest.json  ← PWA কনফিগ
├── scripts/
│   └── bijoy2unicode.py ← বিজয় কনভার্টার
├── vercel.json        ← Vercel কনফিগ
└── requirements.txt   ← Python ডিপেন্ডেন্সি
```

## 💰 ইনকাম

- Google AdSense বসান
- প্রিমিয়াম ফিচার যোগ করুন
- স্পনসরশিপ নিন

## 📝 লাইসেন্স

MIT — ফ্রি ব্যবহার করুন!
