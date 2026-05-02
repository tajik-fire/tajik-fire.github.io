

class ToastService {
  constructor() {
    this.container = null;
    this.toasts = [];
    this.defaultDuration = 5000;
  }

  init() {
    if (this.container) return;
    
    this.container = document.createElement('div');
    this.container.className = 'toast-container';
    document.body.appendChild(this.container);
  }

  createToast(type, title, message, duration = this.defaultDuration) {
    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');

    const icon = this.getIcon(type);
    const toastId = `toast-${Date.now()}`;
    
    toast.innerHTML = `
      ${icon ? `<div class="toast__icon">${icon}</div>` : ''}
      <div class="toast__content">
        ${title ? `<div class="toast__title">${this.escapeHtml(title)}</div>` : ''}
        ${message ? `<div class="toast__message">${this.escapeHtml(message)}</div>` : ''}
      </div>
      <button class="toast__close" aria-label="Close notification" data-toast-id="${toastId}">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12"/>
        </svg>
      </button>
    `;

    this.container.appendChild(toast);
    this.toasts.push({ id: toastId, element: toast });

    const closeBtn = toast.querySelector('.toast__close');
    closeBtn.addEventListener('click', () => this.dismiss(toastId));

    if (duration > 0) {
      setTimeout(() => this.dismiss(toastId), duration);
    }

    return toastId;
  }

  success(title, message, duration) {
    return this.createToast('success', title, message, duration);
  }

  error(title, message, duration) {
    return this.createToast('error', title, message, duration);
  }

  warning(title, message, duration) {
    return this.createToast('warning', title, message, duration);
  }

  info(title, message, duration) {
    return this.createToast('info', title, message, duration);
  }

  dismiss(toastId) {
    const toastIndex = this.toasts.findIndex(t => t.id === toastId);
    if (toastIndex === -1) return;

    const toast = this.toasts[toastIndex].element;
    toast.classList.add('toast--exiting');
    
    toast.addEventListener('animationend', () => {
      toast.remove();
      this.toasts = this.toasts.filter(t => t.id !== toastId);
    }, { once: true });
  }

  dismissAll() {
    this.toasts.forEach(toast => this.dismiss(toast.id));
  }

  getIcon(type) {
    const icons = {
      success: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
        <polyline points="22 4 12 14.01 9 11.01"/>
      </svg>`,
      error: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="15" y1="9" x2="9" y2="15"/>
        <line x1="9" y1="9" x2="15" y2="15"/>
      </svg>`,
      warning: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>`,
      info: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="16" x2="12" y2="12"/>
        <line x1="12" y1="8" x2="12.01" y2="8"/>
      </svg>`
    };
    return icons[type] || '';
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

const toast = new ToastService();
