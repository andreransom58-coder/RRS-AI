# AI News RSS Aggregator

A clean, single-page website that aggregates AI news from multiple RSS feeds.

## Features

- Fetches articles from 5 major AI news sources:
  - OpenAI Blog
  - Hugging Face Blog
  - Google AI Blog
  - DeepMind Blog
  - MIT News AI
- Displays articles in a responsive card layout
- Sorts articles by newest first
- Real-time search/filter by keyword
- Caches feeds for 5 minutes for better performance
- Modern, minimal design with light background
- Fully responsive - works great on mobile devices
- Auto-refreshes every 5 minutes

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd RRS-AI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the Flask development server:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

- **Search**: Type keywords in the search box to filter articles by title, source, or description
- **Refresh**: Click the refresh button to manually fetch the latest articles
- **Read Article**: Click on any article card to open it in a new tab

## API Endpoints

- `GET /` - Main web interface
- `GET /api/articles` - Get cached articles (JSON)
- `GET /api/refresh` - Force refresh all feeds (JSON)

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Libraries**:
  - requests - HTTP requests for fetching feeds
  - python-dateutil - Date parsing
  - xml.etree.ElementTree - Built-in XML/RSS parsing

## Project Structure

```
RRS-AI/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Styles
│   └── js/
│       └── app.js        # Frontend JavaScript
└── README.md             # This file
```

## Configuration

To add or modify RSS feeds, edit the `RSS_FEEDS` dictionary in `app.py`:

```python
RSS_FEEDS = {
    'Feed Name': 'https://example.com/rss.xml',
    # Add more feeds here
}
```

To change cache duration, modify the `CACHE_DURATION` variable in `app.py` (value in seconds).

## License

MIT License
