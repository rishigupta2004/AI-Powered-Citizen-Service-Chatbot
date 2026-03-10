import React from 'react'
import { createRoot } from 'react-dom/client'
import { ClerkProvider } from '@clerk/react'
import App from '../App'
import '../globals.css'
import './i18n' // Initialize i18n
import { supportedLanguages } from './i18n'
import { AuthProvider } from './contexts/AuthContext'

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
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
  console.warn(
    'VITE_CLERK_PUBLISHABLE_KEY not set. Clerk auth UI will be disabled until configured.',
  )
}

root.render(
  <React.StrictMode>
    <ClerkProvider publishableKey={PUBLISHABLE_KEY ?? ''}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </ClerkProvider>
  </React.StrictMode>
)
