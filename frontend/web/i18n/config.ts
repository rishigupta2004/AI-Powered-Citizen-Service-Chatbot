import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: { translation: { title: 'Government Services Portal', search_placeholder: 'Search services, documents, procedures...', search: 'Search', services: 'Services', admin: 'Admin', language: 'Language' } },
  hi: { translation: { title: 'सरकारी सेवाएँ पोर्टल', search_placeholder: 'सेवाएँ, दस्तावेज़, प्रक्रियाएँ खोजें...', search: 'खोज', services: 'सेवाएँ', admin: 'प्रशासन', language: 'भाषा' } },
};

if (!i18n.isInitialized) {
  i18n.use(initReactI18next).init({
    resources,
    lng: 'en',
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
  });
}

export default i18n;

