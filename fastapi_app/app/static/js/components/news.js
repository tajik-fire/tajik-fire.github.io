class NewsManager {
  constructor() {
    this.news = [];
    this.currentPage = 1;
    this.pageSize = 10;
    this.categoryFilter = 'all';
  }

  async init() {
    await this.loadNews();
    this.setupEventListeners();
  }

  async loadNews() {
    try {
      const response = await api.get('/news');
      this.news = response.data || [];
      this.render();
    } catch (error) {
      console.error('Failed to load news:', error);
      this.renderEmptyState('Failed to load news');
    }
  }

  render() {
    this.renderList();
    this.renderPagination();
  }

  renderList() {
    const container = document.getElementById('news-list');
    if (!container) return;

    if (this.news.length === 0) {
      this.renderEmptyState('No news available');
      return;
    }

    const start = (this.currentPage - 1) * this.pageSize;
    const end = start + this.pageSize;
    const pageNews = this.news.slice(start, end);

    container.innerHTML = pageNews.map(item => this.renderNewsItem(item)).join('');

    container.querySelectorAll('.news-item').forEach(item => {
      item.addEventListener('click', () => this.openNewsModal(item.dataset.newsId));
    });
  }

  renderNewsItem(item) {
    const date = new Date(item.published_at || item.created_at).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });

    return `
      <div class="news-item-card" data-news-id="${item.id}">
        <div class="news-item-header">
          <h3 class="news-item-title">${this.escapeHtml(item.title)}</h3>
          <span class="news-item-date">${date}</span>
        </div>
        <div class="news-item-preview">
          ${this.truncateText(item.content, 200)}
        </div>
        <div class="news-item-footer">
          <span class="news-item-author">${this.escapeHtml(item.author_username || 'Admin')}</span>
          <span class="read-more">${_('Read more')} →</span>
        </div>
      </div>
    `;
  }

  renderEmptyState(message) {
    const container = document.getElementById('news-list');
    if (!container) return;

    container.innerHTML = `
      <div class="empty-state">
        <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path>
        </svg>
        <p>${this.escapeHtml(message)}</p>
      </div>
    `;
  }

  renderPagination() {
    const container = document.getElementById('news-pagination');
    if (!container) return;

    const totalPages = Math.ceil(this.news.length / this.pageSize);
    
    if (totalPages <= 1) {
      container.innerHTML = '';
      return;
    }

    let html = '';
    
    html += `
      <button class="pagination-btn" ${this.currentPage === 1 ? 'disabled' : ''} data-page="${this.currentPage - 1}">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>
    `;

    for (let i = 1; i <= totalPages; i++) {
      if (i === 1 || i === totalPages || (i >= this.currentPage - 1 && i <= this.currentPage + 1)) {
        html += `
          <button class="pagination-btn ${i === this.currentPage ? 'active' : ''}" data-page="${i}">
            ${i}
          </button>
        `;
      } else if (i === this.currentPage - 2 || i === this.currentPage + 2) {
        html += `<span class="pagination-btn" style="cursor: default;">...</span>`;
      }
    }

    html += `
      <button class="pagination-btn" ${this.currentPage === totalPages ? 'disabled' : ''} data-page="${this.currentPage + 1}">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      </button>
    `;

    container.innerHTML = html;

    container.querySelectorAll('.pagination-btn[data-page]').forEach(btn => {
      btn.addEventListener('click', () => {
        const page = parseInt(btn.dataset.page);
        if (page >= 1 && page <= totalPages) {
          this.currentPage = page;
          this.renderList();
          this.renderPagination();
          document.getElementById('news-list').scrollIntoView({ behavior: 'smooth' });
        }
      });
    });
  }

  async openNewsModal(newsId) {
    try {
      const news = await api.get(`/news/${newsId}`);
      
      document.getElementById('news-modal-title').textContent = news.title;
      document.getElementById('news-modal-content').innerHTML = this.formatNewsContent(news.content);
      document.getElementById('news-modal-author').textContent = `Author: ${news.author_username || 'Admin'}`;
      document.getElementById('news-modal-date').textContent = new Date(news.published_at || news.created_at).toLocaleString('ru-RU');
      
      modal.open('news-modal');
    } catch (error) {
      console.error('Failed to load news:', error);
      toast.error('Error', 'Failed to load news details');
    }
  }

  formatNewsContent(content) {
    return content
      .split('\n')
      .map(p => p.trim() ? `<p>${this.escapeHtml(p)}</p>` : '')
      .join('');
  }

  setupEventListeners() {
    const createBtn = document.getElementById('create-news-btn');
    if (createBtn) {
      createBtn.addEventListener('click', () => modal.open('create-news-modal'));
    }

    const form = document.getElementById('create-news-form');
    if (form) {
      form.addEventListener('submit', (e) => this.handleCreateNews(e));
    }

    const categoryFilter = document.getElementById('news-category-filter');
    if (categoryFilter) {
      categoryFilter.addEventListener('change', (e) => {
        this.categoryFilter = e.target.value;
        this.applyFilters();
      });
    }
  }

  async handleCreateNews(e) {
    e.preventDefault();
    
    const title = document.getElementById('news-title').value;
    const content = document.getElementById('news-content').value;

    try {
      await api.post('/news', { title, content });
      toast.success('Success', 'News created successfully');
      modal.close('create-news-modal');
      await this.loadNews();
      form.reset();
    } catch (error) {
      console.error('Failed to create news:', error);
      toast.error('Error', error.response?.data?.detail || 'Failed to create news');
    }
  }

  applyFilters() {
    this.currentPage = 1;
    this.render();
  }

  escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }
}

const newsManager = new NewsManager();
