import re

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def chunk_text(text, max_length=500):
    words = text.split()
    chunks = []
    current = []

    for word in words:
        current.append(word)
        if len(current) >= max_length:
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))

    return chunks