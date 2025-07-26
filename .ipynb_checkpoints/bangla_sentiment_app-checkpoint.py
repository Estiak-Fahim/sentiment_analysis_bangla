import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import gradio as gr
import requests
from bs4 import BeautifulSoup 

# Load model and tokenizer
model_path = "Sentiment Project/App/fahim_91_BalDtset.zip"  # Replace with your actual path
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval()

def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = F.softmax(outputs.logits, dim=1).numpy()[0]
    return {
        "Negative": float(probs[0]),
        "Neutral": float(probs[1]),
        "Positive": float(probs[2]),
    }

def extract_and_analyze(url):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        review_divs = soup.find_all("div", class_="other-user-review-text")
        if not review_divs:
            return "No reviews found or selector is incorrect."
        results = []
        for div in review_divs:
            review_text = div.get_text(strip=True)
            if review_text:
                sentiment = predict_sentiment(review_text)
                results.append((review_text, sentiment))
        return results
    except Exception as e:
        return f"Error fetching or parsing the page: {e}"

def process_interface(input_text, url_text):
    if input_text.strip() != "":
        return predict_sentiment(input_text.strip())
    elif url_text.strip() != "":
        return extract_and_analyze(url_text.strip())
    else:
        return "Please enter some review text or a valid URL."

text_input = gr.Textbox(label="✍️ Paste a Bangla Review")
url_input = gr.Textbox(label="🌐 Or paste a Rokomari book link (to auto-analyze all reviews)")

interface = gr.Interface(
    fn=process_interface,
    inputs=[text_input, url_input],
    outputs="json",
    title="📚 Bangla Book Review Sentiment Classifier",
    description="Paste a Bangla review or a Rokomari book link. Get Positive/Negative/Neutral predictions."
)

interface.launch()
