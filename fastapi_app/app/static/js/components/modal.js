

class ModalService {
  constructor() {
    this.activeModals = [];
    this.init();
  }

  init() {
    document.addEventListener('click', (e) => {
      if (e.target.hasAttribute('data-modal-close')) {
        const modal = e.target.closest('.modal');
        if (modal) this.close(modal.id);
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.activeModals.length > 0) {
        this.close(this.activeModals[this.activeModals.length - 1]);
      }
    });
  }

  open(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.setAttribute('aria-hidden', 'false');
    modal.classList.add('modal--active');
    document.body.style.overflow = 'hidden';
    
    this.activeModals.push(modalId);

    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }

    modal.dispatchEvent(new CustomEvent('modal:open', { bubbles: true }));
  }

  close(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.setAttribute('aria-hidden', 'true');
    modal.classList.remove('modal--active');
    
    if (this.activeModals.length === 1) {
      document.body.style.overflow = '';
    }
    
    this.activeModals = this.activeModals.filter(id => id !== modalId);

    modal.dispatchEvent(new CustomEvent('modal:close', { bubbles: true }));
  }

  closeAll() {
    [...this.activeModals].reverse().forEach(id => this.close(id));
  }
}

const modal = new ModalService();
