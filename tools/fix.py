import re

kept_chars_removed = []

with open('merged_english.txt', encoding='utf-8', errors='replace') as f, \
     open('cleaned.txt', 'w', encoding='utf-8') as out:
    for line in f:
        word = line.strip()
        cleaned = re.sub(r'[^a-zA-Z]', '', word)
        if cleaned != word:
            kept_chars_removed.append((word, cleaned))
        if cleaned:
            out.write(cleaned + '\n')

print(f"Modified {len(kept_chars_removed)} lines")
for orig, new in kept_chars_removed[:20]:
    print(f"{orig!r} -> {new!r}")