// Global state
let allArticles = [];
let filteredArticles = [];

// DOM elements
const articlesContainer = document.getElementById('articlesContainer');
const searchInput = document.getElementById('searchInput');
const refreshBtn = document.getElementById('refreshBtn');
const loadingDiv = document.getElementById('loading');
const noResultsDiv = document.getElementById('noResults');
const articleCountSpan = document.getElementById('articleCount');
const lastUpdatedSpan = document.getElementById('lastUpdated');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadArticles();

    // Event listeners
    searchInput.addEventListener('input', handleSearch);
    refreshBtn.addEventListener('click', handleRefresh);
});

// Fetch articles from API
async function loadArticles(refresh = false) {
    try {
        showLoading(true);

        const endpoint = refresh ? '/api/refresh' : '/api/articles';
        const response = await fetch(endpoint);

        if (!response.ok) {
            throw new Error('Failed to fetch articles');
        }

        const data = await response.json();
        allArticles = data.articles;
        filteredArticles = allArticles;

        updateStats(data.count, data.last_updated);
        renderArticles(filteredArticles);

        showLoading(false);
    } catch (error) {
        console.error('Error loading articles:', error);
        showLoading(false);
        articlesContainer.innerHTML = `
            <div class="error" style="grid-column: 1/-1; text-align: center; padding: 40px; color: #e74c3c;">
                <p>Failed to load articles. Please try again later.</p>
            </div>
        `;
    }
}

// Render articles to the DOM
function renderArticles(articles) {
    if (articles.length === 0) {
        articlesContainer.style.display = 'none';
        noResultsDiv.style.display = 'block';
        return;
    }

    articlesContainer.style.display = 'grid';
    noResultsDiv.style.display = 'none';

    articlesContainer.innerHTML = articles.map(article => createArticleCard(article)).join('');

    // Add click handlers to cards
    const cards = articlesContainer.querySelectorAll('.article-card');
    cards.forEach((card, index) => {
        card.addEventListener('click', () => {
            window.open(articles[index].link, '_blank');
        });
    });
}

// Create HTML for article card
function createArticleCard(article) {
    return `
        <div class="article-card">
            <span class="article-source">${escapeHtml(article.source)}</span>
            <h2 class="article-title">${escapeHtml(article.title)}</h2>
            ${article.description ? `<p class="article-description">${escapeHtml(article.description)}</p>` : ''}
            <span class="article-date">${article.date_formatted}</span>
        </div>
    `;
}

// Handle search input
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase().trim();

    if (!searchTerm) {
        filteredArticles = allArticles;
    } else {
        filteredArticles = allArticles.filter(article => {
            const titleMatch = article.title.toLowerCase().includes(searchTerm);
            const sourceMatch = article.source.toLowerCase().includes(searchTerm);
            const descMatch = article.description && article.description.toLowerCase().includes(searchTerm);

            return titleMatch || sourceMatch || descMatch;
        });
    }

    renderArticles(filteredArticles);
    updateArticleCount(filteredArticles.length);
}

// Handle refresh button
async function handleRefresh() {
    refreshBtn.classList.add('spinning');
    await loadArticles(true);
    refreshBtn.classList.remove('spinning');
}

// Update stats display
function updateStats(count, timestamp) {
    updateArticleCount(count);

    if (timestamp) {
        const date = new Date(timestamp * 1000);
        const timeString = date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
        lastUpdatedSpan.textContent = `Last updated: ${timeString}`;
    }
}

// Update article count
function updateArticleCount(count) {
    articleCountSpan.textContent = `${count} article${count !== 1 ? 's' : ''} found`;
}

// Show/hide loading spinner
function showLoading(show) {
    if (show) {
        loadingDiv.style.display = 'block';
        articlesContainer.style.display = 'none';
        noResultsDiv.style.display = 'none';
    } else {
        loadingDiv.style.display = 'none';
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-refresh every 5 minutes
setInterval(() => {
    loadArticles(true);
}, 5 * 60 * 1000);
