import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { SignIn } from '@clerk/clerk-react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../../components/ui/button';
import { Shield } from 'lucide-react';

interface LoginProps {
  onNavigate: (page: string) => void;
}

export function Login({ onNavigate }: LoginProps) {
  const { t } = useTranslation();
  const { isAuthenticated, isLoading } = useAuth();
  const hasClerkKey = Boolean(import.meta.env.VITE_CLERK_PUBLISHABLE_KEY);

  const navigateAfterLogin = () => {
    const redirect = sessionStorage.getItem('redirectAfterLogin');
    if (redirect) {
      sessionStorage.removeItem('redirectAfterLogin');
      onNavigate(redirect === 'apply' ? 'dashboard' : redirect);
      return;
    }
    onNavigate('home');
  };

  useEffect(() => {
    if (isAuthenticated) {
      navigateAfterLogin();
    }
  }, [isAuthenticated]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[var(--surface-2)] via-[var(--background)] to-[var(--surface-3)] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Shield className="w-10 h-10 text-[var(--color-navy)]" />
            <span className="text-2xl font-bold text-[var(--color-navy)]" style={{ fontFamily: 'var(--font-display)' }}>
              {t('common.govtPortal')}
            </span>
          </div>
          <p className="text-[var(--foreground)] opacity-70">{t('login.subtitle')}</p>
        </div>

        <div className="rounded-[var(--radius-2xl)] border border-[var(--border)] bg-[var(--card)] p-4 shadow-[var(--shadow-12)]">
          {hasClerkKey ? (
            <SignIn
              routing="virtual"
              fallbackRedirectUrl={window.location.origin}
              appearance={{
                variables: {
                  colorPrimary: '#000080',
                  colorText: '#111827',
                  colorBackground: '#ffffff',
                  colorInputBackground: '#ffffff',
                  colorInputText: '#111827',
                },
                elements: {
                  cardBox: 'shadow-none bg-[var(--card)]',
                  card: 'shadow-none bg-[var(--card)]',
                  headerTitle: 'text-[var(--foreground)]',
                  headerSubtitle: 'text-[var(--muted-foreground)]',
                  socialButtonsBlockButton: 'border-[var(--border)] bg-[var(--surface-1)] text-[var(--foreground)] hover:bg-[var(--surface-2)]',
                  formFieldInput: 'border-[var(--border)] bg-[var(--input-background)] text-[var(--foreground)]',
                  footerActionText: 'text-[var(--muted-foreground)]',
                  footerActionLink: 'text-[var(--color-navy)]',
                },
              }}
            />
          ) : (
            <div className="space-y-3 p-4 text-center">
              <p className="text-sm text-[var(--muted-foreground)]">{t('login.errors.loginFailed', 'Authentication is unavailable right now.')}</p>
              <Button onClick={() => onNavigate('home')} disabled={isLoading}>{t('navigation.home', 'Home')}</Button>
            </div>
          )}
        </div>

        <p className="text-center text-xs text-[var(--muted-foreground)] mt-6">
          {t('login.terms.text')}{' '}
          <a href="#" className="underline hover:text-[var(--color-navy)]">{t('login.terms.privacy')}</a>
          {' '}{t('login.terms.and')}{' '}
          <a href="#" className="underline hover:text-[var(--color-navy)]">{t('login.terms.terms')}</a>
        </p>
      </div>
    </div>
  );
}

export default Login;
