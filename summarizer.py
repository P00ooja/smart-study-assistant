import requests
import os
from utils import clean_text, chunk_text

SUMMARY_API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"

headers = {
    "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"
}

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