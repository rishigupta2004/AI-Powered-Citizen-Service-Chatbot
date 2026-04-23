import React, { FormEvent, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { SignIn } from '@clerk/clerk-react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Shield } from 'lucide-react';

interface LoginProps {
  onNavigate: (page: string) => void;
}

export function Login({ onNavigate }: LoginProps) {
  const { t } = useTranslation();
  const { isAuthenticated, isLoading, login } = useAuth();
  const hasClerkKey = Boolean(import.meta.env.VITE_CLERK_PUBLISHABLE_KEY);
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  const handleFallbackLogin = async (event: FormEvent) => {
    event.preventDefault();
    if (!identifier.trim() || !password.trim()) {
      setLoginError(t('login.errors.loginFailed', 'Please enter your email/phone and password.'));
      return;
    }

    setLoginError('');
    setIsSubmitting(true);
    try {
      await login(identifier, password);
      navigateAfterLogin();
    } catch (error) {
      const message = error instanceof Error ? error.message : '';
      setLoginError(message || t('login.errors.loginFailed', 'Invalid email or password'));
    } finally {
      setIsSubmitting(false);
    }
  };

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
            <form className="space-y-3 p-4" onSubmit={handleFallbackLogin}>
              <p className="text-sm text-center text-[var(--muted-foreground)]">
                {t(
                  'auth.clerkNotConfigured',
                  'Using backup sign-in. Clerk is not configured on this frontend deployment.'
                )}
              </p>
              <Input
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder={t('login.email', 'Email') + ' / ' + t('login.phone', 'Phone')}
                autoComplete="username"
              />
              <Input
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t('login.password', 'Password')}
                type="password"
                autoComplete="current-password"
              />
              {loginError && <p className="text-sm text-center text-red-600">{loginError}</p>}
              <div className="flex items-center justify-center gap-2">
                <Button type="submit" disabled={isLoading || isSubmitting}>
                  {isSubmitting ? t('common.loading', 'Loading...') : t('navigation.signIn', 'Sign In')}
                </Button>
                <Button type="button" variant="outline" onClick={() => onNavigate('home')} disabled={isLoading || isSubmitting}>
                  {t('navigation.home', 'Home')}
                </Button>
              </div>
            </form>
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
