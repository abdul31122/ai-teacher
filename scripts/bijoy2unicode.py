"""বিজয় → ইউনিকোড কনভার্টার"""

# বিজয় টু ইউনিকোড ম্যাপিং
BIJOY_MAP = {
    'Av': 'অ', 'Aa': 'আ', 'B': 'ই', 'C': 'ঈ', 'D': 'উ', 'E': 'ঊ',
    'F': 'ঋ', 'G': 'এ', 'H': 'ঐ', 'I': 'ও', 'J': 'ঔ',
    'K': 'ক', 'L': 'খ', 'M': 'গ', 'N': 'ঘ', 'O': 'ঙ',
    'P': 'চ', 'Q': 'ছ', 'R': 'জ', 'S': 'ঝ', 'T': 'ঞ',
    'U': 'ট', 'V': 'ঠ', 'W': 'ড', 'X': 'ঢ', 'Y': 'ণ',
    'Z': 'ত', '\\': 'থ', ']': 'দ', '^': 'ধ', '_': 'ন',
    '`': 'প', 'a': 'ফ', 'b': 'ব', 'c': 'ভ', 'd': 'ম',
    'e': 'য', 'f': 'র', 'g': 'ল', 'h': 'শ', 'i': 'ষ',
    'j': 'স', 'k': 'হ', 'l': 'ড়', 'm': 'ঢ়', 'n': 'য়',
    'o': 'ৎ', 'p': 'ং', 'q': 'ঃ', 'r': 'ঁ',
    # কার (vowel signs)
    'v': '্', 'w': 'া', 'x': 'ি', 'y': 'ী', 'z': 'ু',
    '~': 'ূ', '‚': 'ৃ', '†': 'ে', '‡': 'ৈ', 'ˆ': 'ো',
    '‰': 'ৌ',
    # সংখ্যা
    '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
    '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯',
}

def bijoy_to_unicode(text):
    """বিজয় টেক্সট ইউনিকোডে কনভার্ট করে"""
    result = []
    i = 0
    while i < len(text):
        # দুই অক্ষরের ম্যাচ আগে চেক করো
        if i + 1 < len(text) and text[i:i+2] in BIJOY_MAP:
            result.append(BIJOY_MAP[text[i:i+2]])
            i += 2
        elif text[i] in BIJOY_MAP:
            result.append(BIJOY_MAP[text[i]])
            i += 1
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            text = f.read()
        converted = bijoy_to_unicode(text)
        print(converted)
    else:
        print("ব্যবহার: python bijoy2unicode.py <filename>")
