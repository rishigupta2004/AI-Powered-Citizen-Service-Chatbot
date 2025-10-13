import React, { useState, useEffect } from "react";
import {
  Search,
  Globe,
  Menu,
  X,
  Moon,
  Sun,
  Settings as SettingsIcon,
  Contrast,
  ChevronDown,
  User as UserIcon,
  LogOut,
  LogIn,
} from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Logo } from "./Logo";
import { motion, AnimatePresence } from "motion/react";
import { useTheme } from "./ThemeProvider";
import { AccessibilitySettings } from "./AccessibilitySettings";
import { Badge } from "./ui/badge";
import { useAuth } from "./AuthContext";
import { Avatar, AvatarFallback } from "./ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "./ui/popover";

interface NavigationProps {
  onNavigate: (page: string) => void;
  currentPage: string;
  onLoginClick: () => void;
}

export function Navigation({
  onNavigate,
  currentPage,
  onLoginClick,
}: NavigationProps) {
  const { user, isAuthenticated, logout } = useAuth();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [showAccessibilitySettings, setShowAccessibilitySettings] = useState(false);
  const { theme, toggleTheme, isHighContrast } = useTheme();
  const [language, setLanguage] = useState("en");
  const [languageOpen, setLanguageOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (isMobileMenuOpen) setIsMobileMenuOpen(false);
        if (showAccessibilitySettings) setShowAccessibilitySettings(false);
        if (languageOpen) setLanguageOpen(false);
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    window.addEventListener("keydown", handleEscape);

    return () => {
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("keydown", handleEscape);
    };
  }, [isMobileMenuOpen, showAccessibilitySettings, languageOpen]);

  const navItems = [
    { id: "home", label: "Home" },
    { id: "services", label: "Services" },
    { id: "dashboard", label: "My Dashboard" },
    { id: "about", label: "About Us" },
    { id: "faq", label: "FAQ" },
  ];

  const handleNavItemClick = (id: string) => {
    onNavigate(id);
    setIsMobileMenuOpen(false);
  };

  const languages = [
    { code: "en", name: "English", native: "English" },
    { code: "hi", name: "Hindi", native: "हिन्दी" },
    { code: "ta", name: "Tamil", native: "தமிழ்" },
    { code: "te", name: "Telugu", native: "తెలుగు" },
    { code: "bn", name: "Bengali", native: "বাংলা" },
  ];

  const currentLanguage = languages.find(l => l.code === language) || languages[0];

  return (
    <>
      <nav
        className={`fixed top-0 left-0 right-0 z-[var(--z-sticky)] transition-all duration-300 ${
          isScrolled
            ? "glass-effect shadow-[var(--shadow-8)]"
            : "bg-gradient-to-r from-[#000080] to-[#000066] shadow-[var(--shadow-4)]"
        }`}
        role="navigation"
        aria-label="Main navigation"
      >
        <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)]">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <button
              onClick={() => handleNavItemClick("home")}
              className="flex items-center gap-3 group focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring-color)] rounded-[var(--radius-md)] p-2 -m-2"
              aria-label="Go to homepage - Seva Sindhu"
              tabIndex={0}
            >
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
                transition={{
                  type: "spring",
                  stiffness: 400,
                  damping: 17,
                }}
              >
                <Logo
                  size="md"
                  variant={isScrolled ? "color" : "white"}
                  showText={true}
                />
              </motion.div>
            </button>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center gap-[var(--space-2)]">
              {navItems.slice(0, 3).map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleNavItemClick(item.id)}
                  className={`relative px-[var(--space-4)] py-[var(--space-2)] rounded-[var(--radius-md)] transition-all duration-200 font-medium ${
                    currentPage === item.id
                      ? isScrolled
                        ? "text-[#000080] bg-[#000080]/10"
                        : "text-white bg-white/20"
                      : isScrolled
                        ? "text-[var(--foreground)] hover:text-[#000080] hover:bg-[var(--muted)]"
                        : "text-white/80 hover:text-white hover:bg-white/10"
                  }`}
                  aria-current={currentPage === item.id ? "page" : undefined}
                >
                  {item.label}
                  {currentPage === item.id && (
                    <motion.div
                      layoutId="activeTab"
                      className={`absolute bottom-0 left-0 right-0 h-0.5 rounded-full ${
                        isScrolled ? "bg-[#000080]" : "bg-white"
                      }`}
                      initial={false}
                      transition={{
                        type: "spring",
                        stiffness: 500,
                        damping: 30,
                      }}
                    />
                  )}
                </button>
              ))}
            </div>

            {/* Right Side Actions */}
            <div className="flex items-center gap-[var(--space-2)]">
              {/* Search Bar - Desktop */}
              <div className="hidden md:flex items-center relative">
                <label htmlFor="search-input" className="sr-only">
                  Search services
                </label>
                <Search
                  className={`absolute left-3 w-4 h-4 pointer-events-none ${
                    isScrolled ? "text-[var(--muted-foreground)]" : "text-white/60"
                  }`}
                  aria-hidden="true"
                />
                <Input
                  id="search-input"
                  type="search"
                  placeholder="Search services..."
                  className={`pl-10 w-64 h-10 transition-all duration-300 ${
                    isScrolled
                      ? "bg-[var(--input-background)] border-[var(--border)] text-[var(--foreground)]"
                      : "bg-white/10 border-white/20 text-white placeholder:text-white/60"
                  }`}
                  aria-label="Search services"
                />
              </div>

              {/* Language Selector */}
              <Popover open={languageOpen} onOpenChange={setLanguageOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="ghost"
                    className={`h-10 px-3 gap-2 ${
                      isScrolled ? "text-[var(--foreground)]" : "text-white"
                    }`}
                    aria-label="Select language"
                  >
                    <Globe className="w-4 h-4" />
                    <span className="hidden sm:inline">{currentLanguage.native}</span>
                    <ChevronDown className="w-3 h-3" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-56 p-2 bg-[var(--card)] border-[var(--border)]" align="end">
                  <div className="space-y-1">
                    {languages.map((lang) => (
                      <button
                        key={lang.code}
                        onClick={() => {
                          setLanguage(lang.code);
                          setLanguageOpen(false);
                        }}
                        className={`w-full text-left px-3 py-2 rounded-[var(--radius-md)] transition-colors ${
                          language === lang.code
                            ? "bg-[#000080] text-white"
                            : "text-[var(--foreground)] hover:bg-[var(--muted)]"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span>{lang.native}</span>
                          {language === lang.code && (
                            <span className="text-xs">✓</span>
                          )}
                        </div>
                        <div className="text-xs text-current opacity-70">{lang.name}</div>
                      </button>
                    ))}
                  </div>
                </PopoverContent>
              </Popover>

              {/* Theme Toggle */}
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleTheme}
                className={`rounded-full ${
                  isScrolled ? "text-[var(--foreground)]" : "text-white"
                }`}
                aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
              >
                {isHighContrast ? (
                  <Contrast className="w-5 h-5" />
                ) : theme === "dark" ? (
                  <Sun className="w-5 h-5" />
                ) : (
                  <Moon className="w-5 h-5" />
                )}
              </Button>

              {/* Settings Button */}
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowAccessibilitySettings(true)}
                className={`rounded-full ${
                  isScrolled ? "text-[var(--foreground)]" : "text-white"
                }`}
                aria-label="Accessibility settings"
              >
                <SettingsIcon className="w-5 h-5" />
              </Button>

              {/* Login Button - Mobile */}
              {!isAuthenticated && (
                <Button
                  onClick={onLoginClick}
                  size="sm"
                  className={`lg:hidden ${
                    isScrolled
                      ? "bg-[#000080] hover:bg-[#000066] text-white"
                      : "bg-white hover:bg-white/90 text-[#000080]"
                  }`}
                >
                  <LogIn className="w-4 h-4" />
                </Button>
              )}

              {/* Mobile Menu Button */}
              <Button
                variant="ghost"
                size="icon"
                className={`lg:hidden rounded-full ${
                  isScrolled ? "text-[var(--foreground)]" : "text-white"
                }`}
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
                aria-expanded={isMobileMenuOpen}
                aria-controls="mobile-menu"
              >
                {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              id="mobile-menu"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="lg:hidden bg-[var(--card)] border-t border-[var(--border)] shadow-[var(--shadow-8)]"
            >
              <div className="px-[var(--space-4)] py-[var(--space-4)] space-y-[var(--space-2)]">
                {/* Mobile Search */}
                <div className="relative mb-[var(--space-4)]">
                  <label htmlFor="mobile-search-input" className="sr-only">
                    Search services
                  </label>
                  <Search
                    className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--muted-foreground)]"
                    aria-hidden="true"
                  />
                  <Input
                    id="mobile-search-input"
                    type="search"
                    placeholder="Search services..."
                    className="pl-10 w-full bg-[var(--input-background)] text-[var(--foreground)]"
                    aria-label="Search services"
                  />
                </div>

                {/* Mobile Nav Items */}
                {navItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleNavItemClick(item.id)}
                    className={`w-full text-left px-[var(--space-4)] py-[var(--space-3)] rounded-[var(--radius-lg)] transition-all duration-200 font-medium ${
                      currentPage === item.id
                        ? "bg-[#000080] text-white shadow-[var(--shadow-4)]"
                        : "text-[var(--foreground)] hover:bg-[var(--muted)]"
                    }`}
                    aria-current={currentPage === item.id ? "page" : undefined}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Government Emblem Bar */}
        <div className={`border-t ${isScrolled ? "border-[var(--border)]" : "border-white/10"}`}>
          <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)]">
            <div className="flex items-center justify-between h-10">
              <div className="flex items-center gap-2 text-xs">
                <Badge
                  variant="outline"
                  className={`${
                    isScrolled
                      ? "border-[var(--border)] text-[var(--muted-foreground)]"
                      : "border-white/20 text-white/80"
                  }`}
                >
                  🇮🇳 Government of India
                </Badge>
                <span className={`hidden sm:inline ${isScrolled ? "text-[var(--muted-foreground)]" : "text-white/60"}`}>
                  Ministry of Electronics & IT
                </span>
              </div>
              <div className={`text-xs ${isScrolled ? "text-[var(--muted-foreground)]" : "text-white/60"}`}>
                ISO 27001 Certified
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Accessibility Settings Panel */}
      <AccessibilitySettings
        isOpen={showAccessibilitySettings}
        onClose={() => setShowAccessibilitySettings(false)}
      />
    </>
  );
}
