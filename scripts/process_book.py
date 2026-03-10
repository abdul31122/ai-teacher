"""
Book Processor: PDF → Text Chunks → JSON Knowledge Base
Reads PDF, converts Bijoy to Unicode, splits into chapters/lessons,
saves as structured JSON for the AI Teacher.
"""

import json
import re
import sys
import os
import fitz  # PyMuPDF

# Add parent dir for imports
sys.path.insert(0, os.path.dirname(__file__))
from bijoy2unicode import bijoy_to_unicode


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """Extract text from each page of a PDF."""
    doc = fitz.open(pdf_path)
    pages = []
    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text()
        pages.append({
            "page_number": i + 1,
            "raw_text": text,
            "unicode_text": bijoy_to_unicode(text)
        })
    return pages


def detect_lessons(pages: list[dict]) -> list[dict]:
    """Detect lesson boundaries from page text.
    Looks for patterns like: পাঠ—১.১, পাঠ—২.৩, ইউনিট—০১, etc.
    """
    lessons = []
    current_lesson = None
    current_unit = None

    unit_pattern = re.compile(r'ইউনিট[—\-:]\s*(\d+)', re.UNICODE)
    lesson_pattern = re.compile(r'পাঠ[—\-:]\s*(\d+\.?\d*)', re.UNICODE)

    for page in pages:
        text = page["unicode_text"]

        # Check for unit header
        unit_match = unit_pattern.search(text)
        if unit_match:
            current_unit = unit_match.group(1)

        # Check for lesson header
        lesson_match = lesson_pattern.search(text)
        if lesson_match:
            lesson_id = lesson_match.group(1)

            if current_lesson:
                lessons.append(current_lesson)

            current_lesson = {
                "unit": current_unit,
                "lesson_id": lesson_id,
                "start_page": page["page_number"],
                "end_page": page["page_number"],
                "text": text,
            }
        elif current_lesson:
            current_lesson["end_page"] = page["page_number"]
            current_lesson["text"] += "\n" + text

    if current_lesson:
        lessons.append(current_lesson)

    return lessons


def create_chunks(pages: list[dict], chunk_size: int = 1000) -> list[dict]:
    """Create overlapping text chunks for search."""
    chunks = []
    chunk_id = 0

    for page in pages:
        text = page["unicode_text"].strip()
        if not text or len(text) < 50:
            continue

        # Split into chunks with overlap
        words = text.split()
        current_chunk = []
        current_len = 0

        for word in words:
            current_chunk.append(word)
            current_len += len(word) + 1

            if current_len >= chunk_size:
                chunks.append({
                    "id": chunk_id,
                    "page": page["page_number"],
                    "text": " ".join(current_chunk),
                })
                chunk_id += 1
                # Keep last 20% for overlap
                overlap = current_chunk[-(len(current_chunk) // 5):]
                current_chunk = overlap
                current_len = sum(len(w) + 1 for w in current_chunk)

        if current_chunk:
            chunks.append({
                "id": chunk_id,
                "page": page["page_number"],
                "text": " ".join(current_chunk),
            })
            chunk_id += 1

    return chunks


def process_book(pdf_path: str, output_dir: str, book_id: str) -> dict:
    """Full processing pipeline for a book."""
    print(f"📖 Processing: {pdf_path}")

    # Extract text
    print("  📄 Extracting text from PDF...")
    pages = extract_text_from_pdf(pdf_path)
    print(f"  ✅ {len(pages)} pages extracted")

    # Detect lessons
    print("  📚 Detecting lessons...")
    lessons = detect_lessons(pages)
    print(f"  ✅ {len(lessons)} lessons found")

    # Create chunks
    print("  🔍 Creating search chunks...")
    chunks = create_chunks(pages)
    print(f"  ✅ {len(chunks)} chunks created")

    # Book metadata
    book_info = {
        "id": book_id,
        "title": "বাংলা দ্বিতীয় পত্র",
        "subtitle": "ব্যাকরণ",
        "course_code": "SSC-2651",
        "program": "SSC (বাংলাদেশ উন্মুক্ত বিশ্ববিদ্যালয়)",
        "total_pages": len(pages),
        "total_lessons": len(lessons),
        "total_chunks": len(chunks),
    }

    # Save files
    os.makedirs(output_dir, exist_ok=True)

    # Book info
    info_path = os.path.join(output_dir, f"{book_id}_info.json")
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(book_info, f, ensure_ascii=False, indent=2)
    print(f"  💾 Saved: {info_path}")

    # Lessons
    lessons_path = os.path.join(output_dir, f"{book_id}_lessons.json")
    with open(lessons_path, 'w', encoding='utf-8') as f:
        json.dump(lessons, f, ensure_ascii=False, indent=2)
    print(f"  💾 Saved: {lessons_path}")

    # Chunks (for search)
    chunks_path = os.path.join(output_dir, f"{book_id}_chunks.json")
    with open(chunks_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"  💾 Saved: {chunks_path}")

    # Full text (for reference)
    full_text_path = os.path.join(output_dir, f"{book_id}_fulltext.json")
    page_texts = [{"page": p["page_number"], "text": p["unicode_text"]} for p in pages]
    with open(full_text_path, 'w', encoding='utf-8') as f:
        json.dump(page_texts, f, ensure_ascii=False, indent=2)
    print(f"  💾 Saved: {full_text_path}")

    print(f"\n✅ Done! Book '{book_info['title']}' processed successfully!")
    return book_info


if __name__ == "__main__":
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "books", "book.pdf")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    process_book(pdf_path, output_dir, "bangla-2nd-paper")
