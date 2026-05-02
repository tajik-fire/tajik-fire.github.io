

class ApiClient {
  constructor(baseURL = '') {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = new Headers(options.headers || {});

    if (this.token) {
      headers.set('Authorization', `Bearer ${this.token}`);
    }

    if (options.body && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
      options.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.status === 401) {
        return await this.handleUnauthorized(endpoint, options);
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new ApiError(error.detail || 'Request failed', response.status);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }

      return await response.text();
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError('Network error. Please check your connection.', 0);
    }
  }

  async handleUnauthorized(endpoint, options) {
    if (!this.refreshToken) {
      this.logout();
      throw new ApiError('Session expired. Please log in again.', 401);
    }

    try {
      const refreshResponse = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });

      if (!refreshResponse.ok) {
        this.logout();
        throw new ApiError('Session expired. Please log in again.', 401);
      }

      const data = await refreshResponse.json();
      this.setTokens(data.access_token, data.refresh_token);

      const headers = new Headers(options.headers || {});
      headers.set('Authorization', `Bearer ${this.token}`);

      if (options.body && !(options.body instanceof FormData)) {
        headers.set('Content-Type', 'application/json');
        options.body = JSON.stringify(options.body);
      }

      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new ApiError(error.detail || 'Request failed', response.status);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }

      return await response.text();
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError('Network error during token refresh.', 0);
    }
  }

  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }

  post(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'POST', body });
  }

  put(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'PUT', body });
  }

  patch(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'PATCH', body });
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }

  upload(endpoint, formData, options = {}) {
    const headers = options.headers || {};
    delete headers['Content-Type'];
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: formData,
      headers,
    });
  }

  setTokens(accessToken, refreshToken) {
    this.token = accessToken;
    this.refreshToken = refreshToken;
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  logout() {
    this.token = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.dispatchEvent(new CustomEvent('logout'));
  }

  isAuthenticated() {
    return !!this.token;
  }
}

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

const api = new ApiClient('/api');

window.addEventListener('storage', (e) => {
  if (e.key === 'access_token') {
    api.token = e.newValue;
  }
  if (e.key === 'refresh_token') {
    api.refreshToken = e.newValue;
  }
});
