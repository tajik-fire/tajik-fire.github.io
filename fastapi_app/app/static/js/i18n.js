

class I18n {
  constructor() {
    this.currentLang = localStorage.getItem('language') || 'en';
    this.fallbackLang = 'en';
    this.translations = {};
    this.loadedLanguages = new Set();
  }

  async init() {
    await this.loadLanguage(this.currentLang);
    if (this.currentLang !== this.fallbackLang) {
      await this.loadLanguage(this.fallbackLang);
    }
    this.applyTranslations();
    this.setupLanguageSwitcher();
  }

  async loadLanguage(lang) {
    if (this.loadedLanguages.has(lang)) return;

    try {
      const response = await fetch(`/static/locales/${lang}.json`);
      if (!response.ok) throw new Error(`Failed to load ${lang}`);
      this.translations[lang] = await response.json();
      this.loadedLanguages.add(lang);
    } catch (error) {
      console.warn(`Could not load language: ${lang}`, error);
      if (lang !== this.fallbackLang) {
        this.currentLang = this.fallbackLang;
      }
    }
  }

  t(key, params = {}) {
    const keys = key.split('.');
    let value = this.translations[this.currentLang];

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        value = this.getFallbackTranslation(keys);
        break;
      }
    }

    if (typeof value !== 'string') {
      return key;
    }

    return this.interpolate(value, params);
  }

  getFallbackTranslation(keys) {
    if (this.currentLang === this.fallbackLang) return keys.join('.');
    
    let value = this.translations[this.fallbackLang];
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return keys.join('.');
      }
    }
    return value;
  }

  interpolate(text, params) {
    return text.replace(/\{(\w+)\}/g, (match, key) => {
      return params.hasOwnProperty(key) ? params[key] : match;
    });
  }

  applyTranslations() {
    document.documentElement.lang = this.currentLang;
    
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
      const key = el.getAttribute('data-i18n');
      const params = this.parseParams(el);
      el.textContent = this.t(key, params);
    });

    const placeholderElements = document.querySelectorAll('[data-i18n-placeholder]');
    placeholderElements.forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      el.placeholder = this.t(key);
    });

    const titleElements = document.querySelectorAll('[data-i18n-title]');
    titleElements.forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      el.title = this.t(key);
    });
  }

  parseParams(el) {
    const params = {};
    Array.from(el.attributes)
      .filter(attr => attr.name.startsWith('data-i18n-param-'))
      .forEach(attr => {
        const paramName = attr.name.replace('data-i18n-param-', '');
        params[paramName] = attr.value;
      });
    return params;
  }

  setupLanguageSwitcher() {
    const switchers = document.querySelectorAll('[data-language-switch]');
    switchers.forEach(switcher => {
      switcher.addEventListener('click', (e) => {
        e.preventDefault();
        const lang = switcher.getAttribute('data-language-switch');
        this.setLanguage(lang);
      });
    });
  }

  async setLanguage(lang) {
    if (lang === this.currentLang) return;

    localStorage.setItem('language', lang);
    this.currentLang = lang;
    await this.loadLanguage(lang);
    this.applyTranslations();

    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang } }));
  }

  getSupportedLanguages() {
    return [
      { code: 'en', name: 'English', native: 'English' },
      { code: 'ru', name: 'Russian', native: 'Русский' },
      { code: 'tj', name: 'Tajik', native: 'Тоҷикӣ' }
    ];
  }

  getCurrentLanguage() {
    return this.getSupportedLanguages().find(l => l.code === this.currentLang);
  }
}

const i18n = new I18n();

document.addEventListener('DOMContentLoaded', () => {
  i18n.init();
});
