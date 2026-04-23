import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { Contrast, Menu, Moon, Search, Settings as SettingsIcon, Sun, X } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Logo } from "./Logo";
import { useTheme } from "./ThemeProvider";
import { AccessibilitySettings } from "./AccessibilitySettings";
import { LanguageSwitcher } from "../src/components/LanguageSwitcher";
import { ClerkAuthButtons } from "../src/components/auth/ClerkAuthButtons";

interface NavigationProps {
  onNavigate: (page: string) => void;
  currentPage: string;
}

export function Navigation({ onNavigate, currentPage }: NavigationProps) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [showAccessibilitySettings, setShowAccessibilitySettings] = useState(false);
  const shouldReduceMotion = useReducedMotion();
  const { theme, toggleTheme, isHighContrast } = useTheme();
  const { t } = useTranslation();
  const hasClerk = Boolean(import.meta.env.VITE_CLERK_PUBLISHABLE_KEY);

  useEffect(() => {
    const onScroll = () => setIsScrolled(window.scrollY > 12);
    const onEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsMobileMenuOpen(false);
        setShowAccessibilitySettings(false);
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("keydown", onEscape);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("keydown", onEscape);
    };
  }, []);

  const navItems = [
    { id: "home", label: t("navigation.home", "Home") },
    { id: "services", label: t("navigation.services", "Services") },
    { id: "dashboard", label: t("navigation.dashboard", "Dashboard") },
    { id: "about", label: t("navigation.about", "About") },
    { id: "faq", label: t("navigation.faq", "FAQ") },
  ];

  const handleNavigate = (page: string) => {
    onNavigate(page);
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      <nav
        className={`fixed inset-x-0 top-0 z-[var(--z-sticky)] border-b border-[var(--border)] bg-[var(--surface-1)]/95 backdrop-blur-md transition-shadow duration-200 ${
          isScrolled ? "shadow-[var(--shadow-8)]" : "shadow-[var(--shadow-2)]"
        }`}
        role="navigation"
        aria-label={t("navigation.ariaMain", "Main navigation")}
      >
        <div className="border-b border-[#0a2f73] bg-[#0b3d91] text-white">
          <div className="mx-auto flex h-8 max-w-7xl items-center justify-between px-4 text-[11px] sm:px-6 lg:px-8">
            <div className="flex min-w-0 items-center gap-2.5">
              <span className="flex h-3.5 w-5 overflow-hidden rounded-[2px] border border-white/40">
                <span className="h-full flex-1 bg-[#ff9933]" />
                <span className="h-full flex-1 bg-white" />
                <span className="h-full flex-1 bg-[#138808]" />
              </span>
              <span className="truncate">{t("navigation.govStrip", "Government of India | Bharat Sarkar")}</span>
            </div>
            <div className="flex items-center gap-2 sm:gap-3">
              <a
                href="#main-content"
                className="rounded-sm text-white/90 underline-offset-2 hover:text-white hover:underline focus-visible:ring-2 focus-visible:ring-[#ff9933]"
              >
                {t("navigation.skipMain", "Skip to main content")}
              </a>
              <span className="text-white/45">|</span>
              <button
                type="button"
                onClick={() => handleNavigate("faq")}
                className="rounded-sm text-white/90 underline-offset-2 hover:text-white hover:underline focus-visible:ring-2 focus-visible:ring-[#ff9933]"
              >
                {t("common.help", "Help")}
              </button>
            </div>
          </div>
        </div>

        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between gap-3">
            <button
              onClick={() => handleNavigate("home")}
              className="rounded-[var(--radius-md)] p-1.5 transition-colors hover:bg-[var(--surface-2)] focus-visible:ring-2 focus-visible:ring-[var(--focus-ring-color)]"
              aria-label={t("navigation.goHome", "Go to homepage")}
            >
              <Logo size="md" variant="color" showText={true} />
            </button>

            <div className="hidden items-center gap-1.5 lg:flex">
              {navItems.map((item) => {
                const active = currentPage === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleNavigate(item.id)}
                    aria-current={active ? "page" : undefined}
                    className={`relative rounded-[var(--radius-md)] px-3 py-2 text-sm font-medium transition-colors ${
                      active
                        ? "bg-[var(--surface-2)] text-[var(--color-navy)]"
                        : "text-[var(--muted-foreground)] hover:bg-[var(--surface-2)] hover:text-[var(--foreground)]"
                    }`}
                  >
                    {item.label}
                    {active && (
                      <motion.span
                        layoutId="nav-active"
                        className="absolute inset-x-2 -bottom-[2px] h-[2px] rounded-full bg-[var(--color-navy)]"
                        transition={
                          shouldReduceMotion
                            ? { duration: 0 }
                            : { type: "spring", stiffness: 340, damping: 32, mass: 0.85 }
                        }
                      />
                    )}
                  </button>
                );
              })}
            </div>

            <div className="flex items-center gap-1.5 sm:gap-2">
              <div className="relative hidden md:block">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted-foreground)]" />
                <Input
                  id="search-input"
                  type="search"
                  aria-label={t("navigation.searchAria", "Search services")}
                  placeholder={t("navigation.searchPlaceholder", "Search services")}
                  className="h-10 w-60 rounded-[var(--radius-full)] border-[var(--border)] bg-[var(--surface-2)] pl-9 text-sm shadow-none"
                />
              </div>

              <LanguageSwitcher />

              <div className="hidden lg:flex items-center gap-2">
                <ClerkAuthButtons />
                {!hasClerk && (
                  <Button
                    className="rounded-full bg-[var(--color-navy)] px-4 py-2 text-sm font-semibold text-white hover:bg-[var(--color-navy-700)]"
                    onClick={() => handleNavigate("login")}
                  >
                    {t("navigation.signIn", "Sign In")}
                  </Button>
                )}
              </div>

              <Button
                variant="ghost"
                size="icon"
                onClick={toggleTheme}
                aria-label={t("navigation.switchTheme", "Switch theme")}
                className="h-9 w-9 rounded-full text-[var(--muted-foreground)] hover:bg-[var(--surface-2)] hover:text-[var(--foreground)]"
              >
                {isHighContrast ? (
                  <Contrast className="h-4.5 w-4.5" />
                ) : theme === "dark" ? (
                  <Sun className="h-4.5 w-4.5" />
                ) : (
                  <Moon className="h-4.5 w-4.5" />
                )}
              </Button>

              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowAccessibilitySettings(true)}
                aria-label={t("navigation.accessibility", "Accessibility settings")}
                className="h-9 w-9 rounded-full text-[var(--muted-foreground)] hover:bg-[var(--surface-2)] hover:text-[var(--foreground)]"
              >
                <SettingsIcon className="h-4.5 w-4.5" />
              </Button>

              <Button
                variant="ghost"
                size="icon"
                className="h-9 w-9 rounded-full hover:bg-[var(--surface-2)] lg:hidden"
                onClick={() => setIsMobileMenuOpen((prev) => !prev)}
                aria-label={isMobileMenuOpen ? t("navigation.closeMenu", "Close menu") : t("navigation.openMenu", "Open menu")}
                aria-expanded={isMobileMenuOpen}
                aria-controls="mobile-menu"
              >
                {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
            </div>
          </div>
        </div>

        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              id="mobile-menu"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: shouldReduceMotion ? 0 : 0.16 }}
              className="border-t border-[var(--border)] bg-[var(--surface-1)] shadow-[var(--shadow-4)] lg:hidden"
            >
              <div className="space-y-3 px-4 py-4">
                <div className="relative">
                  <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted-foreground)]" />
                  <Input
                    id="mobile-search-input"
                    type="search"
                    aria-label={t("navigation.searchAria", "Search services")}
                    placeholder={t("navigation.searchPlaceholder", "Search services")}
                    className="h-10 w-full rounded-[var(--radius-full)] bg-[var(--surface-2)] pl-9"
                  />
                </div>

                <div className="space-y-1.5">
                  {navItems.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => handleNavigate(item.id)}
                      aria-current={currentPage === item.id ? "page" : undefined}
                      className={`block w-full rounded-[var(--radius-md)] px-3 py-2 text-left text-sm font-medium ${
                        currentPage === item.id
                          ? "bg-[var(--surface-2)] text-[var(--color-navy)]"
                          : "text-[var(--foreground)] hover:bg-[var(--surface-2)]"
                      }`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>

                <div className="pt-2 flex justify-center">
                  <ClerkAuthButtons />
                  {!hasClerk && (
                    <Button onClick={() => handleNavigate("login")}>
                      {t("navigation.signIn", "Sign In")}
                    </Button>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      <AccessibilitySettings isOpen={showAccessibilitySettings} onClose={() => setShowAccessibilitySettings(false)} />
    </>
  );
}
