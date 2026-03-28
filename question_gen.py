import re

def extract_keywords(text):
    words = re.findall(r'\b[A-Za-z]{5,}\b', text.lower())
    freq = {}

    for word in words:
        freq[word] = freq.get(word, 0) + 1

    sorted_words = sorted(freq, key=freq.get, reverse=True)
    return sorted_words[:5]


def get_questions(text):
    try:
        keywords = extract_keywords(text)

        questions = []

        if keywords:
            questions.append(f"What is {keywords[0]} and why is it important?")
        
        if len(keywords) > 1:
            questions.append(f"How does {keywords[1]} affect the overall topic?")
        
        if len(keywords) > 2:
            questions.append(f"What role does {keywords[2]} play in the text?")
        
        questions.append("What is the main idea of the text?")
        questions.append("What conclusion can be drawn from this text?")

        return "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)]), None

    except Exception as e:
        return None, str(e)