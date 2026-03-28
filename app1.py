from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import re
from flask import render_template

load_dotenv()

app = Flask(__name__)

SUMMARY_API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"

headers = {
    "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"
}

@app.route("/")
def home():
    return render_template("index.html")

# 🔹 STEP 1: SUMMARIZATION FUNCTION
# def get_summary(text):
#     payload = {
#         "inputs": text,
#         "parameters": {
#             "max_length": 80,
#             "min_length": 10,
#             "do_sample": False,
#             "no_repeat_ngram_size": 3
#         }
#     }

#     response = requests.post(SUMMARY_API_URL, headers=headers, json=payload)

#     try:
#         result = response.json()
#     except:
#         return None, "Invalid response from model"

#     if isinstance(result, list):
#         summary = result[0].get("summary_text", "")

#         # ✅ Clean summary
#         summary = summary.strip()
#         if not summary.endswith("."):
#             summary += "."

#         return summary, None

#     elif "error" in result:
#         return None, result["error"]
#     else:
#         return None, "Unexpected response"


import re
import requests

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # remove extra spaces
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


def get_summary(text):
    try:
        text = clean_text(text)
        chunks = chunk_text(text)

        summaries = []

        for chunk in chunks:
            payload = {
                "inputs": chunk,
                "parameters": {
                    "max_length": 120,
                    "min_length": 40,
                    "do_sample": False
                }
            }

            response = requests.post(SUMMARY_API_URL, headers=headers, json=payload)
            result = response.json()

            if isinstance(result, list):
                summaries.append(result[0]["summary_text"])

        final_summary = " ".join(summaries)

        return final_summary, None

    except Exception as e:
        return None, str(e)

# # 🔹 STEP 2: QUESTION GENERATION FUNCTION
# def get_questions(text):
#     sentences = text.split(".")
#     questions = []

#     for sentence in sentences:
#         sentence = sentence.strip()
#         if not sentence:
#             continue

#         # Make better questions
#         if " is " in sentence:
#             subject, obj = sentence.split(" is ", 1)
#             questions.append(f"What is {subject.strip()}?")
#         elif " aims to " in sentence:
#             questions.append(f"What is the goal of {sentence.split(' aims to ')[0]}?")
#         elif " focuses on " in sentence:
#             questions.append(f"What does it focus on?")
#         else:
#             questions.append(f"Why is the following important: {sentence}?")

#         if len(questions) == 3:
#             break

#     # If less than 3, add generic question
#     if len(questions) < 3:
#         questions.append("Why is this topic important?")

#     # Format nicely
#     formatted_questions = []
#     for i, q in enumerate(questions, 1):
#         formatted_questions.append(f"{i}. {q.strip()}")

#     return "\n".join(formatted_questions), None

import re

def extract_keywords(text):
    words = re.findall(r'\b[A-Za-z]{5,}\b', text.lower())
    freq = {}

    for word in words:
        freq[word] = freq.get(word, 0) + 1

    # sort by frequency
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

def extract_text_from_image(image_path):
    try:
        import pytesseract
        from PIL import Image
        import os

        # 🔥 Deployment-safe path
        if os.name != "nt":  # not Windows
            pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"

        img = Image.open(image_path)

        # 🔥 Improve OCR accuracy
        img = img.convert("L")

        text = pytesseract.image_to_string(img)

        # remove weird symbols / extra spaces
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # remove non-ascii
        text = re.sub(r'\s+', ' ', text)  # normalize spaces

        return text.strip(), None

    except Exception as e:
        return None, str(e)




# 🔹 FINAL API
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    summary, error = get_summary(text)
    if error:
        return jsonify({"error": error}), 500

    questions, error = get_questions(summary)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({
        "summary": summary,
        "questions": questions
    })

@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files['image']

    # Save temporarily
    image_path = "temp.png"
    image.save(image_path)

    # Step 1: OCR
    text, error = extract_text_from_image(image_path)
    if error:
        return jsonify({"error": error}), 500

    if not text:
        return jsonify({"error": "No text detected"}), 400

    # Step 2: Summary
    summary, error = get_summary(text)
    if error:
        return jsonify({"error": error}), 500

    # Step 3: Questions
    questions, error = get_questions(summary)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({
        "extracted_text": text,
        "summary": summary,
        "questions": questions
    })


if __name__ == "__main__":
    app.run(debug=True)