class AuthManager {
  constructor() {
    this.token = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
    this.user = null;
  }

  async init() {
    if (this.token) {
      try {
        this.user = await this.getCurrentUser();
      } catch (e) {
        await this.logout();
      }
    }
    this.updateUI();
  }

  async register(data) {
    const response = await api.post('/auth/register', data);
    return response.data;
  }

  async login(credentials) {
    const response = await api.post('/auth/login', credentials);
    this.token = response.data.access_token;
    this.refreshToken = response.data.refresh_token;
    localStorage.setItem('access_token', this.token);
    localStorage.setItem('refresh_token', this.refreshToken);
    this.user = await this.getCurrentUser();
    this.updateUI();
    return this.user;
  }

  async logout() {
    this.token = null;
    this.refreshToken = null;
    this.user = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.updateUI();
    window.location.href = '/';
  }

  async refreshTokenFunc() {
    if (!this.refreshToken) return false;
    
    try {
      const response = await api.post('/auth/refresh', { refresh_token: this.refreshToken });
      this.token = response.data.access_token;
      this.refreshToken = response.data.refresh_token;
      localStorage.setItem('access_token', this.token);
      localStorage.setItem('refresh_token', this.refreshToken);
      return true;
    } catch (e) {
      await this.logout();
      return false;
    }
  }

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  }

  async confirmEmail(email, code) {
    const response = await api.post('/auth/confirm-email', { email, code });
    return response.data;
  }

  async resendCode(email) {
    const response = await api.post('/auth/resend-code', { email });
    return response.data;
  }

  async requestPasswordReset(email) {
    const response = await api.post('/auth/reset-password-request', { email });
    return response.data;
  }

  async resetPassword(email, code, newPassword) {
    const response = await api.post('/auth/reset-password-confirm', { email, code, new_password: newPassword });
    return response.data;
  }

  async changePassword(oldPassword, newPassword) {
    const response = await api.post('/auth/change-password', null, {
      params: { old_password: oldPassword, new_password: newPassword }
    });
    return response.data;
  }

  async updateProfile(firstName, lastName) {
    const response = await api.put('/auth/profile', null, {
      params: { first_name: firstName, last_name: lastName }
    });
    this.user = response.data;
    return response.data;
  }

  updateUI() {
    const authElements = document.querySelectorAll('[data-auth]');
    authElements.forEach(el => {
      const authType = el.dataset.auth;
      if (authType === 'logged-in') {
        el.style.display = this.user ? '' : 'none';
      } else if (authType === 'logged-out') {
        el.style.display = this.user ? 'none' : '';
      }
    });

    if (this.user) {
      document.querySelectorAll('[data-user-field]').forEach(el => {
        const field = el.dataset.userField;
        if (field === 'username') el.textContent = this.user.username;
        if (field === 'email') el.textContent = this.user.email;
        if (field === 'first_name') el.textContent = this.user.first_name || '';
        if (field === 'last_name') el.textContent = this.user.last_name || '';
      });
    }
  }

  isAuthenticated() {
    return !!this.token;
  }

  getToken() {
    return this.token;
  }
}

const auth = new AuthManager();
