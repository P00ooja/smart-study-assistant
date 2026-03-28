from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os

from summarizer import get_summary
from question_gen import get_questions
from ocr import extract_text_from_image

load_dotenv()

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data["text"].strip()

    if not text:
        return jsonify({"error": "Empty text"}), 400

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
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({"error": "No selected file"}), 400

    image_path = "temp.png"
    image.save(image_path)

    text, error = extract_text_from_image(image_path)
    if error:
        return jsonify({"error": error}), 500

    if not text:
        return jsonify({"error": "No text detected"}), 400

    summary, error = get_summary(text)
    if error:
        return jsonify({"error": error}), 500

    questions, error = get_questions(summary)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({
        "extracted_text": text,
        "summary": summary,
        "questions": questions
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)