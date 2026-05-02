class LearningManager {
  constructor() {
    this.modules = [];
    this.filteredModules = [];
    this.currentModule = null;
    this.filters = {
      search: '',
      difficulty: 'all'
    };
    this.init();
  }

  async init() {
    await this.loadModules();
    this.setupEventListeners();
  }

  async loadModules() {
    try {
      const response = await api.get('/learning/modules');
      this.modules = response.data || [];
      this.applyFilters();
    } catch (error) {
      console.error('Failed to load modules:', error);
      this.renderEmptyState('Failed to load learning modules');
    }
  }

  applyFilters() {
    let filtered = [...this.modules];

    if (this.filters.search) {
      const searchLower = this.filters.search.toLowerCase();
      filtered = filtered.filter(m => 
        m.title.toLowerCase().includes(searchLower) ||
        (m.description && m.description.toLowerCase().includes(searchLower))
      );
    }

    if (this.filters.difficulty !== 'all') {
      filtered = filtered.filter(m => m.level === this.filters.difficulty);
    }

    this.filteredModules = filtered;
    this.render();
  }

  render() {
    if (this.filteredModules.length === 0) {
      this.renderEmptyState('No modules found');
      return;
    }

    const container = document.getElementById('modules-container');
    if (!container) return;

    container.innerHTML = this.filteredModules.map(module => this.renderModuleCard(module)).join('');

    container.querySelectorAll('.module-card').forEach(card => {
      card.addEventListener('click', () => this.openModuleDetail(card.dataset.moduleId));
    });
  }

  renderModuleCard(module) {
    const levelClass = `module-card__level--${module.level || 'beginner'}`;
    const levelText = module.level ? module.level.charAt(0).toUpperCase() + module.level.slice(1) : 'Beginner';
    
    return `
      <div class="module-card" data-module-id="${module.id}">
        <div class="module-card__header">
          <h3 class="module-card__title">${this.escapeHtml(module.title)}</h3>
          <span class="module-card__level ${levelClass}">${levelText}</span>
        </div>
        <p class="module-card__description">${this.escapeHtml(module.description || '')}</p>
        <div class="module-card__footer">
          <span class="module-card__problems">${module.problemCount || 0} problems</span>
          ${module.enrolled ? '<span class="module-card__enrolled">Enrolled</span>' : ''}
        </div>
      </div>
    `;
  }

  renderEmptyState(message) {
    const container = document.getElementById('modules-container');
    if (!container) return;

    container.innerHTML = `
      <div class="empty-state">
        <svg class="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
        </svg>
        <p>${this.escapeHtml(message)}</p>
      </div>
    `;
  }

  async openModuleDetail(moduleId) {
    try {
      const response = await api.get(`/learning/modules/${moduleId}`);
      this.currentModule = response.data;

      document.getElementById('modal-module-title').textContent = response.data.title;
      document.getElementById('modal-module-description').textContent = response.data.description || '';
      
      const theoryContent = document.getElementById('modal-module-theory');
      if (response.data.theory_content) {
        theoryContent.innerHTML = `
          <h3>Theory</h3>
          <div>${response.data.theory_content}</div>
        `;
        theoryContent.style.display = 'block';
      } else {
        theoryContent.style.display = 'none';
      }

      const problemsList = document.getElementById('problems-list');
      if (response.data.problems && response.data.problems.length > 0) {
        problemsList.innerHTML = response.data.problems.map(problem => `
          <div class="problem-item" onclick="window.location.href='/olympiads/problems/${problem.id}'">
            <div class="problem-item__left">
              <span class="problem-item__id">#${problem.id}</span>
              <span class="problem-item__title">${this.escapeHtml(problem.title)}</span>
            </div>
            <span class="problem-item__difficulty ${problem.difficulty}">${this.capitalize(problem.difficulty)}</span>
          </div>
        `).join('');
      } else {
        problemsList.innerHTML = '<p>No practice problems yet</p>';
      }

      const enrollBtn = document.getElementById('enroll-btn');
      if (response.data.enrolled) {
        enrollBtn.textContent = 'Already Enrolled';
        enrollBtn.disabled = true;
      } else {
        enrollBtn.textContent = 'Enroll';
        enrollBtn.disabled = false;
        enrollBtn.onclick = () => this.enroll(moduleId);
      }

      modal.open('module-detail-modal');
    } catch (error) {
      console.error('Failed to load module:', error);
      toast.error('Error', 'Failed to load module details');
    }
  }

  async enroll(moduleId) {
    try {
      await api.post(`/learning/modules/${moduleId}/enroll`);
      toast.success('Success', 'Successfully enrolled in module');
      this.currentModule.enrolled = true;
      document.getElementById('enroll-btn').textContent = 'Already Enrolled';
      document.getElementById('enroll-btn').disabled = true;
      await this.loadModules();
    } catch (error) {
      console.error('Failed to enroll:', error);
      toast.error('Error', 'Failed to enroll in module');
    }
  }

  setupEventListeners() {
    const searchInput = document.getElementById('module-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.filters.search = e.target.value;
        this.applyFilters();
      });
    }

    const difficultyFilter = document.getElementById('difficulty-filter');
    if (difficultyFilter) {
      difficultyFilter.addEventListener('change', (e) => {
        this.filters.difficulty = e.target.value;
        this.applyFilters();
      });
    }
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

const learningManager = new LearningManager();
