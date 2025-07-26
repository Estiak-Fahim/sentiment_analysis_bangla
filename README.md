# 🔍 Advanced Bangla Book Review Sentiment Classifier

A modern web application for analyzing sentiment in Bangla book reviews with both single review analysis and bulk URL-based scraping capabilities.

## ✨ Features

- **Single Review Analysis**: Analyze individual Bangla review texts instantly
- **Bulk URL Analysis**: Scrape and analyze all reviews from Rokomari book pages
- **Modern UI**: Clean, centered interface with responsive design
- **Real-time Processing**: Instant sentiment classification using pre-trained BERT model
- **Language Detection**: Automatically filters Bangla reviews from scraped content

## 🚀 Quick Start

### Method 1: Using the Launcher (Recommended)
1. Double-click `launch.bat` or run: `python quick_launcher.py`
2. The launcher will automatically install dependencies and start the app

### Method 2: Using the Batch File
1. Double-click `start_app.bat`
2. The application will start automatically

### Method 3: Manual Start
1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `python Bangla_Sentiment_App.py`
3. Open your browser to the displayed URL

## 📋 Requirements

- Python 3.8 or higher
- Internet connection (for URL scraping)
- Bangla BERT model (should be in the correct path)

## 🎯 How to Use

### Single Review Analysis
1. Paste your Bangla review text in the first input box
2. Click "🚀 Analyze Sentiment" or press Enter
3. View the sentiment scores and final verdict with special balanced sentiment logic

### Bulk URL Analysis
1. Copy a Rokomari book URL (e.g., https://www.rokomari.com/book/123456/book-name)
2. Paste it in the second input box
3. Click "🚀 Analyze Sentiment"
4. View the analysis of all scraped Bangla reviews with overall sentiment breakdown

## 📊 Output Format

### Single Review
```json
{
  "total_reviews_analyzed": 1,
  "sentiment_breakdown": {
    "positive_percentage": "65.2%",
    "negative_percentage": "20.1%",
    "neutral_percentage": "14.7%"
  },
  "raw_scores": {
    "Negative": 0.201,
    "Neutral": 0.147,
    "Positive": 0.652
  },
  "final_verdict": "Overall Sentiment: Positive (65.2%)",
  "review_text": "Sample review text..."
}
```

### Bulk Analysis
```json
{
  "total_reviews_analyzed": 25,
  "sentiment_breakdown": {
    "positive_percentage": "48.0%",
    "negative_percentage": "32.0%",
    "neutral_percentage": "20.0%"
  },
  "raw_counts": {
    "Positive": 12,
    "Negative": 8,
    "Neutral": 5
  },
  "final_verdict": "Overall Sentiment: Positive (48.0%)"
}
```

## 🧠 Smart Sentiment Logic

The application includes intelligent sentiment classification:
- **Balanced Sentiment Detection**: If both positive and negative sentiments are within 45-55% range, the final verdict automatically becomes "Neutral"
- **Confidence-based Classification**: Uses the highest confidence score for final determination
- **Bulk Processing**: Analyzes each review individually and aggregates results

## 🛠️ Technical Details

- **Model**: Pre-trained Bangla BERT (Electra) for sequence classification
- **Framework**: Gradio for web interface
- **Scraping**: BeautifulSoup + Rokomari API
- **Language Detection**: langdetect library
- **Smart Port Management**: Automatically finds available ports (starting from 7860)
- **Process Cleanup**: Automatically terminates existing Gradio processes

## 📁 File Structure

```
App/
├── Bangla_Sentiment_App.py       # Main application
├── quick_launcher.py             # Easy launcher script
├── launch.bat                    # Windows batch launcher
├── start_app.bat                 # Alternative batch launcher
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── bangla_bert_model/            # Model directory
    ├── config.json
    ├── model.safetensors
    ├── tokenizer.json
    └── vocab.txt
```

## 🔧 Troubleshooting

1. **Port already in use**: The app automatically finds an available port and terminates existing processes
2. **Model not found**: Ensure the `bangla_bert_model` folder is in the correct location
3. **Dependencies missing**: Run `pip install -r requirements.txt`
4. **Network errors**: Check internet connection for URL scraping
5. **Process conflicts**: The app automatically cleans up existing Gradio processes

## 📝 Notes

- The application processes only Bangla reviews when scraping URLs
- Maximum 50 reviews per URL (configurable in code)
- Results include both raw scores and percentage breakdowns
- Special logic for balanced sentiment detection (45-55% range)
- The interface automatically centers content for better UX
- Supports both single review analysis and bulk URL processing
- Automatic browser opening and public link generation

---

**Developed for advanced Bangla sentiment analysis with modern web interface**
