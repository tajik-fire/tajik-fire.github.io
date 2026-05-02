

class TasksBoard {
  constructor() {
    this.columns = [];
    this.tasks = [];
    this.currentUserId = null;
    this.init();
  }

  async init() {
    await this.loadUser();
    await this.loadColumns();
    await this.loadTasks();
    this.setupEventListeners();
  }

  async loadUser() {
    try {
      const user = await api.get('/users/me');
      this.currentUserId = user.id;
    } catch (error) {
      console.error('Failed to load user:', error);
      toast.error('Error', 'Failed to load user profile');
    }
  }

  async loadColumns() {
    try {
      const response = await api.get('/columns');
      this.columns = response.data || [];
      this.renderColumns();
    } catch (error) {
      console.error('Failed to load columns:', error);
      this.renderEmptyState();
    }
  }

  async loadTasks() {
    try {
      const response = await api.get('/tasks');
      this.tasks = response.data || [];
      this.renderTasks();
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  }

  renderColumns() {
    const container = document.getElementById('board-columns');
    if (!container) return;

    if (this.columns.length === 0) {
      container.innerHTML = `
        <div class="column-empty">
          <svg class="column-empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2"></rect>
            <line x1="9" y1="3" x2="9" y2="21"></line>
          </svg>
          <p class="column-empty-text">No columns yet. Create your first column to get started.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = this.columns.map(column => `
      <div class="column column--${column.id}" data-column-id="${column.id}">
        <header class="column-header">
          <span>${this.escapeHtml(column.title)}</span>
          <span class="column-count" id="count-${column.id}">0</span>
        </header>
        <div class="column-tasks" data-column-id="${column.id}"></div>
      </div>
    `).join('');
  }

  renderTasks() {
    this.columns.forEach(column => {
      const columnTasks = this.tasks.filter(task => task.column_id === column.id);
      const container = document.querySelector(`.column-tasks[data-column-id="${column.id}"]`);
      const countEl = document.getElementById(`count-${column.id}`);
      
      if (!container) return;

      if (countEl) {
        countEl.textContent = columnTasks.length;
      }

      if (columnTasks.length === 0) {
        container.innerHTML = `
          <div class="column-empty">
            <p class="column-empty-text">No tasks</p>
          </div>
        `;
        return;
      }

      container.innerHTML = columnTasks.map(task => this.renderTaskCard(task)).join('');
    });
  }

  renderTaskCard(task) {
    const isOverdue = task.due_date && new Date(task.due_date) < new Date();
    const priorityClass = `task-card-priority--${task.priority || 'medium'}`;
    
    return `
      <div class="task-card" data-task-id="${task.id}" draggable="true">
        <h3 class="task-card-title">${this.escapeHtml(task.title)}</h3>
        ${task.description ? `<p class="task-card-description">${this.escapeHtml(task.description)}</p>` : ''}
        <div class="task-card-meta">
          <span class="task-card-priority ${priorityClass}">
            ${this.capitalize(task.priority || 'medium')}
          </span>
          ${task.due_date ? `
            <span class="task-card-due ${isOverdue ? 'is-overdue' : ''}">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              ${this.formatDate(task.due_date)}
            </span>
          ` : ''}
        </div>
      </div>
    `;
  }

  renderEmptyState() {
    const container = document.getElementById('board-columns');
    if (!container) return;
    
    container.innerHTML = `
      <div class="column-empty">
        <svg class="column-empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2"></rect>
          <line x1="9" y1="3" x2="9" y2="21"></line>
        </svg>
        <p class="column-empty-text">Failed to load board. Please refresh the page.</p>
      </div>
    `;
  }

  setupEventListeners() {
    const createBtn = document.getElementById('create-task-btn');
    if (createBtn) {
      createBtn.addEventListener('click', () => modal.open('task-modal'));
    }

    const form = document.getElementById('task-form');
    if (form) {
      form.addEventListener('submit', (e) => this.handleFormSubmit(e));
    }

    document.addEventListener('modal:close', (e) => {
      if (e.target.id === 'task-modal') {
        form.reset();
      }
    });

    this.setupDragAndDrop();
  }

  setupDragAndDrop() {
    let draggedTask = null;

    document.addEventListener('dragstart', (e) => {
      if (e.target.classList.contains('task-card')) {
        draggedTask = e.target;
        e.target.classList.add('is-dragging');
        e.dataTransfer.effectAllowed = 'move';
      }
    });

    document.addEventListener('dragend', (e) => {
      if (e.target.classList.contains('task-card')) {
        e.target.classList.remove('is-dragging');
        draggedTask = null;
      }
    });

    document.addEventListener('dragover', (e) => {
      e.preventDefault();
      const columnTasks = e.target.closest('.column-tasks');
      if (columnTasks) {
        columnTasks.classList.add('is-drag-over');
      }
    });

    document.addEventListener('dragleave', (e) => {
      const columnTasks = e.target.closest('.column-tasks');
      if (columnTasks && !columnTasks.contains(e.relatedTarget)) {
        columnTasks.classList.remove('is-drag-over');
      }
    });

    document.addEventListener('drop', (e) => {
      e.preventDefault();
      const columnTasks = e.target.closest('.column-tasks');
      if (columnTasks && draggedTask) {
        columnTasks.classList.remove('is-drag-over');
        const newColumnId = columnTasks.dataset.columnId;
        const taskId = draggedTask.dataset.taskId;
        this.moveTask(taskId, newColumnId);
      }
    });
  }

  async moveTask(taskId, newColumnId) {
    try {
      await api.patch(`/tasks/${taskId}`, { column_id: parseInt(newColumnId) });
      toast.success('Success', 'Task moved successfully');
      await this.loadTasks();
    } catch (error) {
      console.error('Failed to move task:', error);
      toast.error('Error', 'Failed to move task');
    }
  }

  async handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = {
      title: document.getElementById('task-title').value,
      description: document.getElementById('task-description').value,
      column_id: parseInt(document.getElementById('task-column').value),
      priority: document.getElementById('task-priority').value,
      assignee_id: document.getElementById('task-assignee').value || null,
      due_date: document.getElementById('task-due-date').value || null
    };

    try {
      await api.post('/tasks', formData);
      toast.success('Success', 'Task created successfully');
      modal.close('task-modal');
      await this.loadTasks();
    } catch (error) {
      console.error('Failed to create task:', error);
      toast.error('Error', error.message || 'Failed to create task');
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

  formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
}

const tasksBoard = new TasksBoard();
