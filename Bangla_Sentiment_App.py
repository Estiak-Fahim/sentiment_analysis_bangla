import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import gradio as gr
import requests
from bs4 import BeautifulSoup
import re
from langdetect import detect
import json
import socket
import subprocess
import sys
import os
import time

def find_available_port(start_port=7860, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def kill_existing_gradio_processes():
    """Kill existing Python processes that might be running Gradio"""
    try:
        if os.name == 'nt':  # Windows
            # Kill processes using common Gradio ports
            for port in range(7860, 7870):
                try:
                    # Find process using the port
                    netstat_result = subprocess.run(['netstat', '-ano'], 
                                                  capture_output=True, text=True, shell=True)
                    if netstat_result.returncode == 0:
                        for line in netstat_result.stdout.split('\n'):
                            if f':{port}' in line and 'LISTENING' in line:
                                parts = line.split()
                                if len(parts) >= 5:
                                    pid = parts[-1]
                                    try:
                                        subprocess.run(['taskkill', '/PID', pid, '/F'], 
                                                     shell=True, capture_output=True)
                                        print(f"Terminated process {pid} using port {port}")
                                    except:
                                        pass
                except:
                    continue
        else:  # Unix/Linux
            subprocess.run(['pkill', '-f', 'gradio'], shell=True)
            print("Terminated existing Gradio processes")
    except Exception as e:
        print(f"Could not terminate existing processes: {e}")

# Load model and tokenizer
model_path = r"C:\Users\User\Sentiment Project\App\Fahim91Model"  
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

def extract_book_id_from_url(url):
    """Extract book ID from Rokomari URL"""
    # Pattern to match book URLs like: https://www.rokomari.com/book/123456/book-name
    pattern = r'https://www\.rokomari\.com/book/(\d+)/'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def scrape_rokomari_reviews(book_id, max_reviews=50):
    """Scrape reviews from Rokomari using the API endpoint"""
    try:
        # Get reviews using the API directly
        reviews_url = f"https://www.rokomari.com/productreviews/{book_id}/2000"
        reviews_response = requests.get(reviews_url)
        
        if reviews_response.status_code != 200:
            return {"error": "Failed to fetch reviews"}
        
        reviews_data = reviews_response.json()
        
        bangla_reviews = []
        processed_count = 0
        
        for review_item in reviews_data:
            if processed_count >= max_reviews:
                break
                
            review_text = review_item.get('reviewDetail', '').strip()
            if not review_text:
                continue
            
            try:
                # Check if the review is in Bangla
                detected_lang = detect(review_text)
                if detected_lang == 'bn':
                    bangla_reviews.append(review_text)
                    processed_count += 1
            except:
                # If language detection fails, still include the review
                bangla_reviews.append(review_text)
                processed_count += 1
        
        return {"reviews": bangla_reviews}
        
    except Exception as e:
        return {"error": f"Error scraping reviews: {str(e)}"}

def process_interface(input_text, url_text):
    input_text = input_text.strip()
    url_text = url_text.strip()

    if input_text and url_text:
        return {"error": "Please provide either a review text or a URL, not both."}
    elif input_text:
        # Get sentiment prediction for single review
        sentiment_result = predict_sentiment(input_text)
        
        # Convert to percentage format for consistency
        sentiment_percentages = {
            sentiment: round(score * 100, 1)
            for sentiment, score in sentiment_result.items()
        }
        
        # Determine final verdict with special condition for balanced sentiment
        positive_pct = sentiment_percentages['Positive']
        negative_pct = sentiment_percentages['Negative']
        
        # If both positive and negative are within 45-55% range, verdict is neutral
        if (45 <= positive_pct <= 55) and (45 <= negative_pct <= 55):
            final_verdict = "Neutral"
        else:
            final_verdict = max(sentiment_percentages, key=sentiment_percentages.get)
        
        return {
            "total_reviews_analyzed": 1,
            "sentiment_breakdown": {
                "positive_percentage": f"{sentiment_percentages['Positive']}%",
                "negative_percentage": f"{sentiment_percentages['Negative']}%", 
                "neutral_percentage": f"{sentiment_percentages['Neutral']}%"
            },
            "raw_scores": sentiment_result,
            "final_verdict": f"Overall Sentiment: {final_verdict} ({sentiment_percentages[final_verdict]}%)",
            "review_text": input_text[:100] + "..." if len(input_text) > 100 else input_text
        }
    elif url_text:
        # Extract book ID from URL
        book_id = extract_book_id_from_url(url_text)
        if not book_id:
            return {"error": "Invalid Rokomari URL. Please provide a valid book URL like: https://www.rokomari.com/book/123456/book-name"}
        
        # Scrape reviews and classify each one individually in the background
        scraped_data = scrape_rokomari_reviews(book_id)
        if "error" in scraped_data:
            return scraped_data
        
        # Process only the review texts for classification
        reviews = scraped_data["reviews"]
        if not reviews:
            return {"error": "No Bangla reviews found for this book"}
        
        # Count sentiments in background processing
        sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        total_reviews = len(reviews)
        
        # Process each review in background
        for review_text in reviews:
            sentiment_result = predict_sentiment(review_text)
            dominant_sentiment = max(sentiment_result, key=sentiment_result.get)
            sentiment_counts[dominant_sentiment] += 1
        
        # Calculate percentages
        sentiment_percentages = {
            sentiment: round((count / total_reviews) * 100, 1)
            for sentiment, count in sentiment_counts.items()
        }
        
        # Determine final verdict with special condition for balanced sentiment
        positive_pct = sentiment_percentages['Positive']
        negative_pct = sentiment_percentages['Negative']
        
        # If both positive and negative are within 45-55% range, verdict is neutral
        if (45 <= positive_pct <= 55) and (45 <= negative_pct <= 55):
            final_verdict = "Neutral"
        else:
            final_verdict = max(sentiment_percentages, key=sentiment_percentages.get)
        
        return {
            "total_reviews_analyzed": total_reviews,
            "sentiment_breakdown": {
                "positive_percentage": f"{sentiment_percentages['Positive']}%",
                "negative_percentage": f"{sentiment_percentages['Negative']}%", 
                "neutral_percentage": f"{sentiment_percentages['Neutral']}%"
            },
            "raw_counts": sentiment_counts,
            "final_verdict": f"Overall Sentiment: {final_verdict} ({sentiment_percentages[final_verdict]}%)",
        }
    else:
        return {"message": "Please enter some review text or a valid Rokomari book URL."}

# Create the Gradio interface with custom CSS for centered layout
css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.title {
    text-align: center;
    color: #2c3e50;
    margin-bottom: 20px;
}

.description {
    text-align: center;
    color: #34495e;
    margin-bottom: 40px;
    line-height: 1.6;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

/* Force center alignment for input container */
.input-container {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    margin: 20px auto !important;
}

/* Center the textboxes */
.input-container .gr-textbox,
.input-container .gradio-textbox {
    max-width: 500px !important;
    width: 100% !important;
    margin: 10px auto !important;
}

/* Center the button */
.center-button {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    margin: 20px auto !important;
    width: 100% !important;
}

.center-button button {
    margin: 0 auto !important;
}

/* Output styling */
.output-json {
    margin-top: 30px;
    max-height: 500px;
    overflow-y: auto;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

/* Force center alignment for the main content */
.main-content {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    max-width: 600px !important;
    margin: 0 auto !important;
}
"""

with gr.Blocks(css=css, title="Bangla Sentiment Classifier") as interface:
    gr.HTML("""
        <div class="title">
            <h1>Advanced Bangla Book Review Sentiment Classifier</h1>
        </div>
    """)
    
    gr.HTML("""
        <div class="description">
            <p> Paste a Bangla review text or Paste a Rokomari book URL to get instant sentiment analysis</p>
            <br>
        </div>
    """)
    
    # Properly centered input section
    with gr.Column(elem_classes=["main-content"]):
        with gr.Group(elem_classes=["input-container"]):
            text_input = gr.Textbox(
                label="📝 Paste a Bangla Review", 
                placeholder="Type your Bangla review here...",
                lines=3
            )
            
            url_input = gr.Textbox(
                label="🔗 Or paste a Rokomari book URL", 
                placeholder="https://www.rokomari.com/book/123456/book-name",
                lines=1
            )
            
            submit_btn = gr.Button("🚀 Analyze Sentiment", variant="primary", size="lg", elem_classes=["center-button"])
    
    # Centered output
    output = gr.JSON(
        label="Analysis Results",
        elem_classes=["output-json"]
    )
    
    submit_btn.click(
        fn=process_interface,
        inputs=[text_input, url_input],
        outputs=output
    )
    
    # Auto-submit on Enter key for better UX
    text_input.submit(
        fn=process_interface,
        inputs=[text_input, url_input],
        outputs=output
    )
    
    url_input.submit(
        fn=process_interface,
        inputs=[text_input, url_input],
        outputs=output
    )

if __name__ == "__main__":
    print("⇛ Starting Bangla Sentiment Analysis App...")
    
    # Kill existing Gradio processes
    print("⇛ Cleaning up existing sessions...")
    kill_existing_gradio_processes()
    
    # Wait a moment for ports to be freed
    print("⇛ Waiting for ports to be freed...")
    time.sleep(3)
    
    # Find available port
    available_port = find_available_port()
    if available_port is None:
        print("❌ Could not find available port. Please close other applications and try again.")
        sys.exit(1)
    
    print(f"⇛ Using port {available_port}")
    print("⇛ Generating public shareable link...")

    try:
        interface.launch(
            server_name="0.0.0.0",  # Allow external access
            server_port=available_port,  # Use dynamically found port
            share=True,  # Creates a public Gradio link
            inbrowser=True,  # Automatically opens in browser
            show_error=True,
            quiet=False,  # Show startup messages
            debug=False  # Disable debug mode for production
        )
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)