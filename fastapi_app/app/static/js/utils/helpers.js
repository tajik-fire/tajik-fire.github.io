

export function formatDate(date, locale = 'en') {
  if (!date) return '';
  
  const d = new Date(date);
  const now = new Date();
  const diffMs = now - d;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  const diffWeeks = Math.floor(diffDays / 7);
  const diffMonths = Math.floor(diffDays / 30);
  const diffYears = Math.floor(diffDays / 365);

  const translations = {
    en: { justNow: 'Just now', m: 'm ago', h: 'h ago', d: 'd ago', w: 'w ago', mo: 'mo ago', y: 'y ago' },
    ru: { justNow: 'Только что', m: 'м назад', h: 'ч назад', d: 'д назад', w: 'н назад', mo: 'мес назад', y: 'л назад' },
    es: { justNow: 'Justo ahora', m: 'm hace', h: 'h hace', d: 'd hace', w: 's hace', mo: 'meses hace', y: 'años hace' }
  };

  const t = translations[locale] || translations.en;

  if (diffMins < 1) return t.justNow;
  if (diffMins < 60) return `${diffMins}${t.m}`;
  if (diffHours < 24) return `${diffHours}${t.h}`;
  if (diffDays < 7) return `${diffDays}${t.d}`;
  if (diffWeeks < 4) return `${diffWeeks}${t.w}`;
  if (diffMonths < 12) return `${diffMonths}${t.mo}`;
  return `${diffYears}${t.y}`;
}

export function formatDateTime(date, options = {}) {
  if (!date) return '';
  
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  };

  return new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options }).format(new Date(date));
}

export function truncate(str, length = 50, suffix = '...') {
  if (!str) return '';
  if (str.length <= length) return str;
  return str.slice(0, length) + suffix;
}

export function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export function throttle(func, limit = 300) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

export function classNames(...classes) {
  return classes.filter(Boolean).join(' ');
}

export function generateId() {
  return Math.random().toString(36).substring(2, 15) + 
         Math.random().toString(36).substring(2, 15);
}

export function getInitials(name) {
  if (!name) return '?';
  const parts = name.trim().split(' ');
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

export function copyToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text);
  }
  
  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.style.position = 'fixed';
  textArea.style.left = '-999999px';
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  
  return new Promise((resolve, reject) => {
    try {
      document.execCommand('copy');
      resolve();
    } catch (err) {
      reject(err);
    }
    document.body.removeChild(textArea);
  });
}

export function downloadFile(data, filename, type = 'application/json') {
  const blob = new Blob([data], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

export function parseQueryString(queryString) {
  const params = {};
  const queries = queryString.substring(1).split('&');
  
  queries.forEach(item => {
    const [key, value] = item.split('=');
    if (key) {
      params[decodeURIComponent(key)] = value ? decodeURIComponent(value) : '';
    }
  });
  
  return params;
}

export function buildQueryString(params) {
  return Object.entries(params)
    .filter(([_, value]) => value !== undefined && value !== null)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');
}

export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function retry(fn, retries = 3, delay = 1000) {
  return async (...args) => {
    let lastError;
    
    for (let i = 0; i < retries; i++) {
      try {
        return await fn(...args);
      } catch (error) {
        lastError = error;
        if (i < retries - 1) {
          await sleep(delay * Math.pow(2, i));
        }
      }
    }
    
    throw lastError;
  };
}
