class ProblemsArchive {
  constructor() {
    this.problems = [];
    this.filteredProblems = [];
    this.currentPage = 1;
    this.pageSize = 20;
    this.filters = {
      search: '',
      difficulties: ['easy', 'medium', 'hard'],
      tags: [],
      status: 'all',
      sort: 'id_asc'
    };
    this.viewMode = 'list';
    this.init();
  }

  async init() {
    await this.loadProblems();
    this.setupEventListeners();
  }

  async loadProblems() {
    try {
      const response = await api.get('/olympiads/problems');
      this.problems = response.data || [];
      this.extractTags();
      this.applyFilters();
    } catch (error) {
      console.error('Failed to load problems:', error);
      this.renderEmptyState('Failed to load problems');
    }
  }

  extractTags() {
    const tagSet = new Set();
    this.problems.forEach(problem => {
      if (problem.tags && Array.isArray(problem.tags)) {
        problem.tags.forEach(tag => tagSet.add(tag));
      }
    });
    this.allTags = Array.from(tagSet).sort();
    this.renderTagsFilter();
  }

  renderTagsFilter() {
    const container = document.getElementById('tags-filter');
    if (!container || !this.allTags.length) return;

    container.innerHTML = this.allTags.map(tag => `
      <span class="tag-chip" data-tag="${this.escapeHtml(tag)}">${this.escapeHtml(tag)}</span>
    `).join('');

    container.querySelectorAll('.tag-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        chip.classList.toggle('active');
        const tag = chip.dataset.tag;
        if (chip.classList.contains('active')) {
          if (!this.filters.tags.includes(tag)) {
            this.filters.tags.push(tag);
          }
        } else {
          this.filters.tags = this.filters.tags.filter(t => t !== tag);
        }
        this.applyFilters();
      });
    });
  }

  applyFilters() {
    let filtered = [...this.problems];

    if (this.filters.search) {
      const searchLower = this.filters.search.toLowerCase();
      filtered = filtered.filter(p => 
        p.title.toLowerCase().includes(searchLower) ||
        String(p.id).includes(searchLower)
      );
    }

    if (this.filters.difficulties.length > 0) {
      filtered = filtered.filter(p => 
        this.filters.difficulties.includes(p.difficulty)
      );
    }

    if (this.filters.tags.length > 0) {
      filtered = filtered.filter(p => 
        p.tags && p.tags.some(tag => this.filters.tags.includes(tag))
      );
    }

    if (this.filters.status !== 'all') {
      filtered = filtered.filter(p => {
        const userStatus = p.user_status || 'unsolved';
        if (this.filters.status === 'solved') return userStatus === 'solved';
        if (this.filters.status === 'attempted') return userStatus === 'attempted';
        if (this.filters.status === 'unsolved') return userStatus === 'unsolved';
        return true;
      });
    }

    switch (this.filters.sort) {
      case 'id_asc':
        filtered.sort((a, b) => a.id - b.id);
        break;
      case 'id_desc':
        filtered.sort((a, b) => b.id - a.id);
        break;
      case 'difficulty_asc':
        const diffOrder = { easy: 0, medium: 1, hard: 2 };
        filtered.sort((a, b) => diffOrder[a.difficulty] - diffOrder[b.difficulty]);
        break;
      case 'difficulty_desc':
        const diffOrderDesc = { easy: 2, medium: 1, hard: 0 };
        filtered.sort((a, b) => diffOrderDesc[a.difficulty] - diffOrderDesc[b.difficulty]);
        break;
      case 'solved_count':
        filtered.sort((a, b) => (b.solved_count || 0) - (a.solved_count || 0));
        break;
    }

    this.filteredProblems = filtered;
    this.currentPage = 1;
    this.render();
  }

  render() {
    this.renderCount();
    this.renderProblems();
    this.renderPagination();
  }

  renderCount() {
    const countEl = document.getElementById('problems-count');
    if (countEl) {
      countEl.textContent = this.filteredProblems.length;
    }
  }

  renderProblems() {
    const container = document.getElementById('problems-list');
    if (!container) return;

    if (this.filteredProblems.length === 0) {
      this.renderEmptyState('No problems found');
      return;
    }

    const start = (this.currentPage - 1) * this.pageSize;
    const end = start + this.pageSize;
    const pageProblems = this.filteredProblems.slice(start, end);

    if (this.viewMode === 'list') {
      container.className = 'problems-table';
      container.innerHTML = pageProblems.map(p => this.renderProblemRow(p)).join('');
    } else {
      container.className = 'problems-grid';
      container.innerHTML = pageProblems.map(p => this.renderProblemCard(p)).join('');
    }

    container.querySelectorAll('.problem-item').forEach(item => {
      item.addEventListener('click', () => this.openProblemModal(item.dataset.problemId));
    });
  }

  renderProblemRow(problem) {
    const difficultyClass = `difficulty--${problem.difficulty}`;
    const statusIcon = this.getStatusIcon(problem.user_status);
    
    return `
      <div class="problem-row problem-item" data-problem-id="${problem.id}">
        <span class="problem-id">#${problem.id}</span>
        <span class="problem-title">${this.escapeHtml(problem.title)}</span>
        <span class="problem-difficulty">
          <span class="difficulty-badge ${difficultyClass}">${this.capitalize(problem.difficulty)}</span>
        </span>
        <span class="problem-solved">${problem.solved_count || 0}</span>
        <span class="problem-status">
          ${statusIcon}
        </span>
      </div>
    `;
  }

  renderProblemCard(problem) {
    const difficultyClass = `difficulty--${problem.difficulty}`;
    
    return `
      <div class="problem-card problem-item" data-problem-id="${problem.id}">
        <div class="problem-card-header">
          <span class="problem-id">#${problem.id}</span>
          <span class="difficulty-badge ${difficultyClass}">${this.capitalize(problem.difficulty)}</span>
        </div>
        <h3 class="problem-card-title">${this.escapeHtml(problem.title)}</h3>
        <div class="problem-card-footer">
          <span class="problem-card-solved">${problem.solved_count || 0} solved</span>
          ${this.getMiniStatusIcon(problem.user_status)}
        </div>
      </div>
    `;
  }

  getStatusIcon(status) {
    if (status === 'solved') {
      return `
        <svg class="status-icon status-icon--solved" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
      `;
    } else if (status === 'attempted') {
      return `
        <svg class="status-icon status-icon--attempted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      `;
    }
    return '';
  }

  getMiniStatusIcon(status) {
    if (status === 'solved') {
      return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    } else if (status === 'attempted') {
      return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#eab308" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
    }
    return '';
  }

  renderEmptyState(message) {
    const container = document.getElementById('problems-list');
    if (!container) return;

    container.className = 'problems-table';
    container.innerHTML = `
      <div class="empty-state">
        <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <p>${this.escapeHtml(message)}</p>
      </div>
    `;
  }

  renderPagination() {
    const container = document.getElementById('pagination');
    if (!container) return;

    const totalPages = Math.ceil(this.filteredProblems.length / this.pageSize);
    
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
          this.renderProblems();
          this.renderPagination();
          document.getElementById('problems-list').scrollIntoView({ behavior: 'smooth' });
        }
      });
    });
  }

  async openProblemModal(problemId) {
    try {
      const problem = await api.get(`/olympiads/problems/${problemId}`);
      
      document.getElementById('problem-modal-title').textContent = `#${problem.id} - ${problem.title}`;
      
      const content = document.getElementById('problem-modal-content');
      content.innerHTML = `
        <div class="problem-statement">
          <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem;">
            <span class="difficulty-badge difficulty--${problem.difficulty}">${this.capitalize(problem.difficulty)}</span>
            ${problem.time_limit ? `<span class="tag-chip">⏱ ${problem.time_limit}s</span>` : ''}
            ${problem.memory_limit ? `<span class="tag-chip">💾 ${problem.memory_limit}MB</span>` : ''}
          </div>
          
          <h3>${_('Problem Statement')}</h3>
          <p>${problem.description || ''}</p>
          
          <h3>${_('Input Format')}</h3>
          <p>${problem.input_format || ''}</p>
          
          <h3>${_('Output Format')}</h3>
          <p>${problem.output_format || ''}</p>
          
          ${problem.examples && problem.examples.length > 0 ? `
            <h3>${_('Examples')}</h3>
            ${problem.examples.map((ex, i) => `
              <div class="example-block">
                <div class="example-title">${_('Example')} ${i + 1}</div>
                <div class="example-io">
                  <div><span class="example-label">${_('Input')}:</span>${ex.input}</div>
                  <div><span class="example-label">${_('Output')}:</span>${ex.output}</div>
                  ${ex.explanation ? `<div style="margin-top: 0.5rem; color: var(--text-secondary);">${ex.explanation}</div>` : ''}
                </div>
              </div>
            `).join('')}
          ` : ''}
          
          ${problem.tags && problem.tags.length > 0 ? `
            <h3>${_('Tags')}</h3>
            <div class="tags-list" style="margin-top: 0.5rem;">
              ${problem.tags.map(tag => `<span class="tag-chip">${this.escapeHtml(tag)}</span>`).join('')}
            </div>
          ` : ''}
        </div>
      `;
      
      document.getElementById('solve-problem-btn').href = `/olympiads/problems/${problem.id}/submit`;
      modal.open('problem-modal');
    } catch (error) {
      console.error('Failed to load problem:', error);
      toast.error('Error', 'Failed to load problem details');
    }
  }

  setupEventListeners() {
    const searchInput = document.getElementById('problem-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.filters.search = e.target.value;
        this.applyFilters();
      });
    }

    document.querySelectorAll('.filter-checkbox[data-filter="difficulty"]').forEach(checkbox => {
      checkbox.addEventListener('change', (e) => {
        const value = e.target.value;
        if (e.target.checked) {
          if (!this.filters.difficulties.includes(value)) {
            this.filters.difficulties.push(value);
          }
        } else {
          this.filters.difficulties = this.filters.difficulties.filter(d => d !== value);
        }
        this.applyFilters();
      });
    });

    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
      statusFilter.addEventListener('change', (e) => {
        this.filters.status = e.target.value;
        this.applyFilters();
      });
    }

    const sortFilter = document.getElementById('sort-filter');
    if (sortFilter) {
      sortFilter.addEventListener('change', (e) => {
        this.filters.sort = e.target.value;
        this.applyFilters();
      });
    }

    const resetBtn = document.getElementById('reset-filters');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => this.resetFilters());
    }

    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        this.viewMode = e.currentTarget.dataset.view;
        this.renderProblems();
      });
    });
  }

  resetFilters() {
    this.filters = {
      search: '',
      difficulties: ['easy', 'medium', 'hard'],
      tags: [],
      status: 'all',
      sort: 'id_asc'
    };

    document.getElementById('problem-search').value = '';
    document.querySelectorAll('.filter-checkbox[data-filter="difficulty"]').forEach(cb => {
      cb.checked = true;
    });
    document.getElementById('status-filter').value = 'all';
    document.getElementById('sort-filter').value = 'id_asc';
    document.querySelectorAll('.tag-chip').forEach(chip => {
      chip.classList.remove('active');
    });

    this.applyFilters();
  }

  escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
}

const problemsArchive = new ProblemsArchive();
