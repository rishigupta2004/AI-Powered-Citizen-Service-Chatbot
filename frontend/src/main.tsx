import React from 'react'
import { createRoot } from 'react-dom/client'
import App from '../App'
import '../globals.css'
import './i18n' // Initialize i18n
import { supportedLanguages } from './i18n'

// Apply RTL direction on initial load
const savedLang = localStorage.getItem('i18nextLng');
if (savedLang) {
  const lang = supportedLanguages.find(l => l.code === savedLang);
  if (lang?.rtl) {
    document.documentElement.dir = 'rtl';
  }
}

const container = document.getElementById('root')!
const root = createRoot(container)
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
