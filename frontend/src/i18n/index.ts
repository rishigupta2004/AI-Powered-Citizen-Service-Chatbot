import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import enTranslations from "./locales/en/translation.json";
import hiTranslations from "./locales/hi/translation.json";

const resources = {
  en: {
    translation: enTranslations,
  },
  hi: {
    translation: hiTranslations,
  },
};

export const supportedLanguages = [
  { code: "en", label: "English", nativeLabel: "English", script: "Latin", rtl: false },
  { code: "hi", label: "Hindi", nativeLabel: "हिन्दी", script: "Devanagari", rtl: false },
  { code: "bn", label: "Bengali", nativeLabel: "বাংলা", script: "Bengali", rtl: false },
  { code: "ta", label: "Tamil", nativeLabel: "தமிழ்", script: "Tamil", rtl: false },
  { code: "te", label: "Telugu", nativeLabel: "తెలుగు", script: "Telugu", rtl: false },
  { code: "mr", label: "Marathi", nativeLabel: "मराठी", script: "Devanagari", rtl: false },
  { code: "gu", label: "Gujarati", nativeLabel: "ગુજરાતી", script: "Gujarati", rtl: false },
  { code: "pa", label: "Punjabi", nativeLabel: "ਪੰਜਾਬੀ", script: "Gurmukhi", rtl: false },
  { code: "kn", label: "Kannada", nativeLabel: "ಕನ್ನಡ", script: "Kannada", rtl: false },
  { code: "ml", label: "Malayalam", nativeLabel: "മലയാളം", script: "Malayalam", rtl: false },
  { code: "or", label: "Odia", nativeLabel: "ଓଡ଼ିଆ", script: "Odia", rtl: false },
  { code: "as", label: "Assamese", nativeLabel: "অসমীয়া", script: "Bengali", rtl: false },
  { code: "ur", label: "Urdu", nativeLabel: "اردو", script: "Arabic", rtl: true },
  { code: "ks", label: "Kashmiri", nativeLabel: "کٲشُر", script: "Arabic", rtl: true },
  { code: "sd", label: "Sindhi", nativeLabel: "سنڌي", script: "Arabic", rtl: true },
  { code: "sa", label: "Sanskrit", nativeLabel: "संस्कृतं", script: "Devanagari", rtl: false },
  { code: "ne", label: "Nepali", nativeLabel: "नेपाली", script: "Devanagari", rtl: false },
  { code: "kok", label: "Konkani", nativeLabel: "कोंकणी", script: "Devanagari", rtl: false },
  { code: "mai", label: "Maithili", nativeLabel: "मैथिली", script: "Devanagari", rtl: false },
  { code: "doi", label: "Dogri", nativeLabel: "डोगरी", script: "Devanagari", rtl: false },
  { code: "mni", label: "Manipuri", nativeLabel: "মণিপুরি", script: "Bengali", rtl: false },
  { code: "sat", label: "Santali", nativeLabel: "संताली", script: "Ol Chiki", rtl: false },
];

export const changeLanguage = async (langCode: string) => {
  const lang = supportedLanguages.find(l => l.code === langCode);
  if (!lang) return;
  
  if (!i18n.hasResourceBundle(langCode, "translation")) {
    const translations = await import(`./locales/${langCode}/translation.json`);
    i18n.addResourceBundle(langCode, "translation", translations.default);
  }
  
  await i18n.changeLanguage(langCode);
  document.documentElement.lang = langCode;
  document.documentElement.dir = lang.rtl ? 'rtl' : 'ltr';
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "en",
    debug: import.meta.env.DEV,

    interpolation: {
      escapeValue: false,
    },

    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
    },
  });

export default i18n;
