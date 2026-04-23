import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import {
  Menu,
  X,
  Moon,
  Sun,
  Settings as SettingsIcon,
  ChevronRight,
} from "lucide-react";
import { Button } from "./ui/button";
import { Logo } from "./Logo";
import { motion, AnimatePresence } from "framer-motion";
import { useTheme } from "./ThemeProvider";
import { AccessibilitySettings } from "./AccessibilitySettings";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "./ui/popover";
import { LanguageSwitcher } from "./LanguageSwitcher";

interface NavigationProps {
  onNavigate: (page: string) => void;
  currentPage: string;
}

export function Navigation({
  onNavigate,
  currentPage,
}: NavigationProps) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const { t } = useTranslation();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 40);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navItems = [
    { id: "home", label: t("navigation.home") || "Home" },
    { id: "services", label: t("navigation.services") || "Services" },
    { id: "dashboard", label: t("navigation.dashboard") || "Dashboard" },
    { id: "about", label: t("navigation.about") || "About Us" },
    { id: "faq", label: t("navigation.faq") || "FAQ" },
  ];

  const handleNavItemClick = (id: string) => {
    onNavigate(id);
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-[100] transition-all duration-500 w-full flex flex-col">
        
        {/* Government Top Bar - Clean UX4G Compliant */}
        <div 
          className={`w-full bg-[#1e293b] text-white py-1.5 transition-all duration-300 hidden md:block ${
            isScrolled ? "h-0 opacity-0 overflow-hidden py-0" : "h-8 opacity-100"
          }`}
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center text-[11px] font-medium h-full">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-2 text-slate-200">
                <span className="flex gap-[1px]">
                  <span className="w-2 h-2.5 bg-saffron rounded-l-sm"></span>
                  <span className="w-2 h-2.5 bg-white"></span>
                  <span className="w-2 h-2.5 bg-green rounded-r-sm"></span>
                </span>
                Government of India | भारत सरकार
              </span>
              <a href="#main-content" className="hover:text-white text-slate-400 transition-colors outline-none focus-visible:ring-2 focus-visible:ring-saffron rounded px-1">
                Skip to main content
              </a>
            </div>
            
            <div className="flex items-center gap-3">
              <LanguageSwitcher />
              <div className="flex items-center gap-2 border-l border-slate-600 pl-3">
                <button 
                  onClick={() => toggleTheme()} 
                  className="text-slate-300 hover:text-white transition-colors focus-visible:ring-2 focus-visible:ring-saffron outline-none rounded p-1"
                  aria-label="Toggle theme"
                >
                  {theme === 'dark' ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
                </button>
                <Popover>
                  <PopoverTrigger asChild>
                    <button className="text-slate-300 hover:text-white transition-colors focus-visible:ring-2 focus-visible:ring-saffron outline-none rounded p-1" aria-label="Accessibility settings">
                      <SettingsIcon className="w-3.5 h-3.5" />
                    </button>
                  </PopoverTrigger>
                  <PopoverContent className="w-80 p-0 border-0 shadow-2xl rounded-2xl bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl" align="end">
                    <AccessibilitySettings />
                  </PopoverContent>
                </Popover>
              </div>
            </div>
          </div>
        </div>

        {/* Floating Pill Navigation */}
        <div className={`w-full flex justify-center transition-all duration-500 ${isScrolled ? "pt-4 px-4" : "pt-0 bg-white/90 dark:bg-slate-950/90 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-800/50"}`}>
          <div className={`transition-all duration-500 w-full ${
            isScrolled 
              ? "max-w-5xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-2xl border border-white/40 dark:border-slate-700/50 shadow-lg shadow-navy/5 rounded-full px-6" 
              : "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
          }`}>
            <div className={`flex justify-between items-center transition-all duration-500 ${isScrolled ? "h-16" : "h-20"}`}>
              {/* Logo */}
              <button
                onClick={() => handleNavItemClick("home")}
                className="flex items-center gap-3 focus-visible:ring-2 focus-visible:ring-saffron outline-none rounded-xl p-1 -ml-1"
              >
                <Logo size={isScrolled ? "sm" : "md"} variant="color" showText={true} />
              </button>

              {/* Desktop Nav Links */}
              <nav className="hidden lg:flex items-center relative gap-1">
                {navItems.map((item) => {
                  const isActive = currentPage === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => handleNavItemClick(item.id)}
                      className={`relative px-4 py-2 text-sm font-semibold transition-colors rounded-full focus-visible:ring-2 focus-visible:ring-saffron outline-none ${
                        isActive 
                          ? "text-blue-700 dark:text-blue-400" 
                          : "text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white"
                      }`}
                    >
                      {isActive && (
                        <motion.div
                          layoutId="nav-indicator"
                          className="absolute inset-0 bg-blue-50 dark:bg-blue-900/30 rounded-full -z-10"
                          transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                        />
                      )}
                      {item.label}
                    </button>
                  );
                })}
              </nav>

              {/* Action Buttons */}
              <div className="hidden lg:flex items-center gap-3">
                <Button 
                  variant="ghost" 
                  className={`font-semibold rounded-full transition-colors ${isScrolled ? "h-10 px-4" : "h-11 px-5"}`}
                  onClick={() => onNavigate('admin')}
                >
                  Admin
                </Button>
                <Button 
                  className={`font-semibold rounded-full bg-navy hover:bg-blue-800 text-white shadow-md hover:shadow-lg transition-all ${isScrolled ? "h-10 px-6" : "h-11 px-8"}`}
                  onClick={() => onNavigate('login')}
                >
                  Sign In
                </Button>
              </div>

              {/* Mobile Toggle */}
              <div className="lg:hidden flex items-center">
                <button
                  onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                  className="text-slate-700 dark:text-slate-300 p-2 focus-visible:ring-2 focus-visible:ring-saffron rounded-full outline-none"
                >
                  {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Menu Dropdown */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed inset-x-0 top-[104px] z-[90] bg-white/95 dark:bg-slate-950/95 backdrop-blur-xl border-b border-slate-200 dark:border-slate-800 shadow-xl lg:hidden p-6"
          >
            <div className="flex flex-col gap-2">
              {navItems.map((item, i) => (
                <motion.button
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  key={item.id}
                  onClick={() => handleNavItemClick(item.id)}
                  className={`w-full flex items-center justify-between px-5 py-4 rounded-2xl font-semibold text-lg transition-all ${
                    currentPage === item.id
                      ? "bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                      : "text-slate-700 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-900"
                  }`}
                >
                  {item.label}
                  {currentPage === item.id && <ChevronRight className="w-5 h-5" />}
                </motion.button>
              ))}
              <div className="h-px bg-slate-200/50 dark:bg-slate-800/50 my-4" />
              <Button className="w-full h-14 rounded-2xl font-bold text-lg bg-navy" onClick={() => onNavigate('login')}>
                Sign In
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
