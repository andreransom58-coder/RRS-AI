from flask import Flask, render_template, jsonify
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import time
import threading
import re

app = Flask(__name__)

# RSS feed sources for AI news
RSS_FEEDS = {
    'OpenAI Blog': 'https://openai.com/blog/rss.xml',
    'Hugging Face Blog': 'https://huggingface.co/blog/feed.xml',
    'Google AI Blog': 'https://blog.research.google/feeds/posts/default',
    'DeepMind Blog': 'https://deepmind.google/blog/rss.xml',
    'MIT News AI': 'https://news.mit.edu/rss/topic/artificial-intelligence2'
}

# Cache configuration
CACHE_DURATION = 300  # 5 minutes in seconds
cache = {
    'articles': [],
    'last_updated': None
}
cache_lock = threading.Lock()


def parse_date(date_string):
    """Parse various date formats to datetime object"""
    if not date_string:
        return datetime.now()

    try:
        # Try parsing with dateutil
        return date_parser.parse(date_string)
    except:
        try:
            # Fallback to time struct
            return datetime(*date_string[:6])
        except:
            return datetime.now()


def strip_html_tags(text):
    """Remove HTML tags from text"""
    if not text:
        return ''
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def fetch_feed(feed_name, feed_url):
    """Fetch and parse a single RSS feed"""
    articles = []
    try:
        # Fetch the feed
        response = requests.get(feed_url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; AI-News-Aggregator/1.0)'
        })
        response.raise_for_status()

        # Parse XML
        root = ET.fromstring(response.content)

        # Handle both RSS and Atom feeds
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }

        # Check if it's an Atom feed
        if root.tag == '{http://www.w3.org/2005/Atom}feed':
            entries = root.findall('atom:entry', namespaces)
            for entry in entries[:10]:
                title_elem = entry.find('atom:title', namespaces)
                link_elem = entry.find('atom:link[@rel="alternate"]', namespaces) or entry.find('atom:link', namespaces)
                published_elem = entry.find('atom:published', namespaces) or entry.find('atom:updated', namespaces)
                summary_elem = entry.find('atom:summary', namespaces) or entry.find('atom:content', namespaces)

                title = title_elem.text if title_elem is not None else 'No Title'
                link = link_elem.get('href', '#') if link_elem is not None else '#'
                pub_date_str = published_elem.text if published_elem is not None else ''
                description = summary_elem.text if summary_elem is not None else ''

                # Parse date
                date_obj = parse_date(pub_date_str) if pub_date_str else datetime.now()

                # Clean description
                description = strip_html_tags(description)
                description = description[:200] + '...' if len(description) > 200 else description

                articles.append({
                    'title': title,
                    'link': link,
                    'source': feed_name,
                    'date': date_obj.isoformat(),
                    'date_formatted': date_obj.strftime('%b %d, %Y'),
                    'description': description.strip()
                })
        else:
            # RSS feed
            items = root.findall('.//item')
            for item in items[:10]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                pub_date_elem = item.find('pubDate') or item.find('dc:date', namespaces)
                description_elem = item.find('description') or item.find('content:encoded', namespaces)

                title = title_elem.text if title_elem is not None else 'No Title'
                link = link_elem.text if link_elem is not None else '#'
                pub_date_str = pub_date_elem.text if pub_date_elem is not None else ''
                description = description_elem.text if description_elem is not None else ''

                # Parse date
                date_obj = parse_date(pub_date_str) if pub_date_str else datetime.now()

                # Clean description
                description = strip_html_tags(description)
                description = description[:200] + '...' if len(description) > 200 else description

                articles.append({
                    'title': title,
                    'link': link,
                    'source': feed_name,
                    'date': date_obj.isoformat(),
                    'date_formatted': date_obj.strftime('%b %d, %Y'),
                    'description': description.strip()
                })

    except Exception as e:
        print(f"Error fetching {feed_name}: {str(e)}")

    return articles


def fetch_all_feeds():
    """Fetch all RSS feeds and cache results"""
    all_articles = []

    # Fetch all feeds
    for feed_name, feed_url in RSS_FEEDS.items():
        articles = fetch_feed(feed_name, feed_url)
        all_articles.extend(articles)

    # Sort by date (newest first)
    all_articles.sort(key=lambda x: x['date'], reverse=True)

    # Update cache
    with cache_lock:
        cache['articles'] = all_articles
        cache['last_updated'] = time.time()

    return all_articles


def get_cached_articles():
    """Get articles from cache or fetch if cache is expired"""
    with cache_lock:
        # Check if cache is valid
        if cache['last_updated'] is None or \
           (time.time() - cache['last_updated']) > CACHE_DURATION:
            # Cache expired or doesn't exist
            pass
        else:
            # Return cached articles
            return cache['articles']

    # Fetch fresh articles
    return fetch_all_feeds()


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/articles')
def get_articles():
    """API endpoint to get articles"""
    articles = get_cached_articles()
    return jsonify({
        'articles': articles,
        'count': len(articles),
        'last_updated': cache['last_updated']
    })


@app.route('/api/refresh')
def refresh_feeds():
    """API endpoint to force refresh feeds"""
    articles = fetch_all_feeds()
    return jsonify({
        'articles': articles,
        'count': len(articles),
        'refreshed': True
    })


if __name__ == '__main__':
    # Fetch feeds on startup
    print("Fetching initial feed data...")
    fetch_all_feeds()
    print(f"Loaded {len(cache['articles'])} articles")

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
