import React, { useState, useEffect } from "react";
import { ThemeProvider } from "./components/ThemeProvider";
import { Navigation } from "./components/Navigation";
import { Footer } from "./components/Footer";
import { AdvancedChatbot } from "./components/AdvancedChatbot";
import { EnhancedHome } from "./components/pages/EnhancedHome";
import { ServicesPage } from "./components/pages/ServicesPage";
import { ServiceDetail } from "./components/pages/ServiceDetail";
import { FAQPage } from "./components/pages/FAQPage";
import { AboutPage } from "./components/pages/AboutPage";
import { AdminPortalPage } from "./components/pages/AdminPortalPage";
import { UserDashboard } from "./components/pages/UserDashboard";
import { ApplicationTracker } from "./components/pages/ApplicationTracker";
import { Login } from "./src/pages/Login";
import { Toaster } from "./components/ui/sonner";
import { toast } from "sonner";
import { ArrowUp } from "lucide-react";
import { Button } from "./components/ui/button";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useAuthContext } from "./src/contexts/AuthContext";
import { useTranslation } from "react-i18next";

type ClerkWindow = Window & {
  Clerk?: {
    openSignIn?: (opts?: { redirectUrl?: string }) => void;
  };
};

function AppContent() {
  const shouldReduceMotion = useReducedMotion();
  const { isAuthenticated } = useAuthContext();
  const { t } = useTranslation();
  const [currentPage, setCurrentPage] = useState("home");
  const [currentServiceId, setCurrentServiceId] =
    useState<string>("passport_seva");
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [wasAuthenticated, setWasAuthenticated] = useState(isAuthenticated);

  useEffect(() => {
    // Set page title
    document.title =
      "Seva Sindhu - Government of India Citizen Services Portal";

    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 400);
    };
    window.addEventListener("scroll", handleScroll);
    return () =>
      window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (isAuthenticated && !wasAuthenticated) {
      const redirect = sessionStorage.getItem("redirectAfterLogin");
      sessionStorage.removeItem("redirectAfterLogin");
      
      const target = redirect === "apply" ? "dashboard" : (redirect || "dashboard");
      setCurrentPage(target);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
    setWasAuthenticated(isAuthenticated);
  }, [isAuthenticated, wasAuthenticated]);

  const openAuthModal = (targetPage: string) => {
    sessionStorage.setItem("redirectAfterLogin", targetPage);
    const hasClerkKey = Boolean(import.meta.env.VITE_CLERK_PUBLISHABLE_KEY);
    if (hasClerkKey) {
      const clerk = (window as ClerkWindow).Clerk;
      if (clerk?.openSignIn) {
        clerk.openSignIn({ redirectUrl: window.location.href });
        return;
      }
    }
    toast.info(t("auth.signInRequired", "Please sign in to continue."));
    setCurrentPage("login");
  };

  const handleNavigate = (page: string, serviceId?: string) => {
    const protectedPages = new Set(["dashboard", "tracker", "apply"]);
    if (protectedPages.has(page) && !isAuthenticated) {
      openAuthModal(page);
      return;
    }

    const resolvedPage = page === "apply" ? "dashboard" : page;
    setCurrentPage(resolvedPage);
    if (serviceId) {
      setCurrentServiceId(serviceId);
    }
    window.scrollTo({ top: 0, behavior: "smooth" });

    // Announce page change to screen readers
    const announcement = t("app.navigatedTo", "Navigated to {{page}} page", {
      page,
    });
    const liveRegion = document.getElementById("live-region");
    if (liveRegion) {
      liveRegion.textContent = announcement;
    }
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const renderPage = () => {
    switch (currentPage) {
      case "home":
        return <EnhancedHome onNavigate={handleNavigate} />;
      case "services":
        return <ServicesPage onNavigate={handleNavigate} />;
      case "service-detail":
        return (
          <ServiceDetail
            onNavigate={handleNavigate}
            serviceId={currentServiceId}
          />
        );
      case "dashboard":
        if (!isAuthenticated) {
          return <Login onNavigate={handleNavigate} />;
        }
        return <UserDashboard onNavigate={handleNavigate} />;
      case "tracker":
        if (!isAuthenticated) {
          return <Login onNavigate={handleNavigate} />;
        }
        return (
          <ApplicationTracker onNavigate={handleNavigate} />
        );
      case "login":
        return <Login onNavigate={handleNavigate} />;
      case "faq":
        return <FAQPage onNavigate={handleNavigate} />;
      case "about":
        return <AboutPage onNavigate={handleNavigate} />;
      case "admin":
        return <AdminPortalPage onNavigate={handleNavigate} />;
      default:
        return <EnhancedHome onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      {/* Skip to Main Content Link */}
        <a
          href="#main-content"
          className="skip-link"
          tabIndex={0}
        >
          {t("navigation.skipMain", "Skip to main content")}
        </a>

      {/* Live Region for Screen Reader Announcements */}
      <div
        id="live-region"
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      />

      {/* Navigation */}
      <Navigation
        onNavigate={handleNavigate}
        currentPage={currentPage}
      />

      {/* Main Content */}
      <main
        id="main-content"
        role="main"
        className="relative"
        tabIndex={-1}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={`${currentPage}-${currentServiceId}`}
            initial={shouldReduceMotion ? false : { opacity: 0, y: 12 }}
            animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
            exit={shouldReduceMotion ? undefined : { opacity: 0, y: -8 }}
            transition={{ duration: shouldReduceMotion ? 0 : 0.28, ease: [0.22, 1, 0.36, 1] }}
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Footer */}
      <Footer onNavigate={handleNavigate} />

      {/* Advanced AI Chatbot - Context Aware */}
      <AdvancedChatbot 
        onNavigate={handleNavigate} 
        currentPage={currentPage}
        currentService={currentServiceId}
      />

      {/* Scroll to Top Button */}
      {showScrollTop && (
        <Button
          onClick={scrollToTop}
          size="icon"
          className="fixed bottom-24 left-6 z-[var(--z-fixed)] w-12 h-12 rounded-full bg-[var(--card)] border-2 border-[var(--border)] shadow-[var(--shadow-8)] hover:shadow-[var(--shadow-12)] hover:-translate-y-1 transition-all"
          aria-label={t("app.scrollTop", "Scroll to top")}
        >
          <ArrowUp className="w-5 h-5 text-[var(--primary)]" />
        </Button>
      )}

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "var(--card)",
            color: "var(--card-foreground)",
            border: "1px solid var(--border)",
          },
        }}
      />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
