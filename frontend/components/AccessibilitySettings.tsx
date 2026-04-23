import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Settings,
  Type,
  Eye,
  Globe,
  X,
  Check,
  Info,
  Minus,
  Plus,
  Moon,
  Sun,
  Contrast,
  RotateCcw,
} from "lucide-react";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Switch } from "./ui/switch";
import { Slider } from "./ui/slider";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Separator } from "./ui/separator";
import { Alert, AlertDescription } from "./ui/alert";
import { useTheme } from "./ThemeProvider";

interface AccessibilitySettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AccessibilitySettings({
  isOpen,
  onClose,
}: AccessibilitySettingsProps) {
  const { theme, setTheme, isHighContrast, toggleHighContrast } = useTheme();
  const [fontSize, setFontSize] = useState(100);
  const [language, setLanguage] = useState("en");
  const [reducedMotion, setReducedMotion] = useState(false);
  const [screenReaderAnnouncements, setScreenReaderAnnouncements] = useState(true);

  useEffect(() => {
    // Load saved settings
    const savedFontSize = localStorage.getItem("fontSize");
    const savedLanguage = localStorage.getItem("language");
    const savedReducedMotion = localStorage.getItem("reducedMotion") === "true";
    const savedScreenReader = localStorage.getItem("screenReader") !== "false";

    if (savedFontSize) setFontSize(parseInt(savedFontSize));
    if (savedLanguage) setLanguage(savedLanguage);
    setReducedMotion(savedReducedMotion);
    setScreenReaderAnnouncements(savedScreenReader);
  }, []);

  useEffect(() => {
    // Apply font size
    document.documentElement.style.fontSize = `${fontSize}%`;
    localStorage.setItem("fontSize", fontSize.toString());
  }, [fontSize]);

  useEffect(() => {
    // Apply reduced motion
    if (reducedMotion) {
      document.documentElement.style.setProperty("--transition-fast", "0ms");
      document.documentElement.style.setProperty("--transition-base", "0ms");
      document.documentElement.style.setProperty("--transition-slow", "0ms");
    } else {
      document.documentElement.style.setProperty("--transition-fast", "150ms");
      document.documentElement.style.setProperty("--transition-base", "200ms");
      document.documentElement.style.setProperty("--transition-slow", "250ms");
    }
    localStorage.setItem("reducedMotion", reducedMotion.toString());
  }, [reducedMotion]);

  useEffect(() => {
    localStorage.setItem("language", language);
  }, [language]);

  useEffect(() => {
    localStorage.setItem("screenReader", screenReaderAnnouncements.toString());
  }, [screenReaderAnnouncements]);

  const resetSettings = () => {
    setFontSize(100);
    setLanguage("en");
    setReducedMotion(false);
    setScreenReaderAnnouncements(true);
    setTheme("light");
    if (isHighContrast) toggleHighContrast();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-[var(--z-modal-backdrop)] bg-black/50 backdrop-blur-sm"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Slide-in Panel */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 bottom-0 z-[var(--z-modal)] w-full max-w-md bg-[var(--card)] border-l-2 border-[var(--border)] shadow-2xl overflow-y-auto"
            role="dialog"
            aria-labelledby="accessibility-title"
            aria-modal="true"
          >
            {/* Header */}
            <div className="sticky top-0 z-10 flex items-center justify-between p-6 bg-gradient-to-br from-[#000080] to-[#000066] border-b border-white/10">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-[var(--radius-xl)] flex items-center justify-center">
                  <Settings className="w-6 h-6 text-white" aria-hidden="true" />
                </div>
                <div>
                  <h2
                    id="accessibility-title"
                    className="text-2xl font-bold text-white"
                  >
                    Settings
                  </h2>
                  <p className="text-sm text-white/80">
                    Customize your experience
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="rounded-full text-white hover:bg-white/10"
                aria-label="Close settings"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            <div className="p-6 space-y-8">
              {/* Information Alert */}
              <Alert className="border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-950/20">
                <Info className="w-5 h-5 text-blue-600" aria-hidden="true" />
                <AlertDescription className="text-[var(--foreground)]">
                  Your preferences are saved automatically and applied across all pages.
                </AlertDescription>
              </Alert>

              {/* Theme & Contrast */}
              <div className="space-y-4" role="group" aria-labelledby="theme-label">
                <div className="flex items-center gap-3">
                  <Eye className="w-5 h-5 text-[var(--muted-foreground)]" aria-hidden="true" />
                  <div>
                    <Label id="theme-label" className="text-base font-semibold text-[var(--foreground)]">
                      Appearance
                    </Label>
                    <p className="text-sm text-[var(--muted-foreground)]">
                      Choose your color scheme
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    onClick={() => {
                      setTheme("light");
                      if (isHighContrast) toggleHighContrast();
                    }}
                    className={`relative p-4 rounded-[var(--radius-xl)] border-2 transition-all ${
                      theme === "light" && !isHighContrast
                        ? "border-[#000080] bg-[#000080]/5 shadow-[var(--shadow-4)]"
                        : "border-[var(--border)] hover:border-[var(--border-strong)]"
                    }`}
                    aria-pressed={theme === "light" && !isHighContrast}
                    aria-label="Light theme"
                  >
                    <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-white border border-gray-200 flex items-center justify-center shadow-sm">
                      <Sun className="w-6 h-6 text-yellow-500" aria-hidden="true" />
                    </div>
                    <div className="text-sm font-medium text-center text-[var(--foreground)]">
                      Light
                    </div>
                    {theme === "light" && !isHighContrast && (
                      <div className="absolute top-2 right-2 w-5 h-5 bg-[#000080] rounded-full flex items-center justify-center">
                        <Check className="w-3 h-3 text-white" />
                      </div>
                    )}
                  </button>

                  <button
                    onClick={() => {
                      setTheme("dark");
                      if (isHighContrast) toggleHighContrast();
                    }}
                    className={`relative p-4 rounded-[var(--radius-xl)] border-2 transition-all ${
                      theme === "dark" && !isHighContrast
                        ? "border-[#000080] bg-[#000080]/5 shadow-[var(--shadow-4)]"
                        : "border-[var(--border)] hover:border-[var(--border-strong)]"
                    }`}
                    aria-pressed={theme === "dark" && !isHighContrast}
                    aria-label="Dark theme"
                  >
                    <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-gray-800 border border-gray-700 flex items-center justify-center shadow-sm">
                      <Moon className="w-6 h-6 text-blue-400" aria-hidden="true" />
                    </div>
                    <div className="text-sm font-medium text-center text-[var(--foreground)]">
                      Dark
                    </div>
                    {theme === "dark" && !isHighContrast && (
                      <div className="absolute top-2 right-2 w-5 h-5 bg-[#000080] rounded-full flex items-center justify-center">
                        <Check className="w-3 h-3 text-white" />
                      </div>
                    )}
                  </button>

                  <button
                    onClick={toggleHighContrast}
                    className={`relative p-4 rounded-[var(--radius-xl)] border-2 transition-all ${
                      isHighContrast
                        ? "border-[#000080] bg-[#000080]/5 shadow-[var(--shadow-4)]"
                        : "border-[var(--border)] hover:border-[var(--border-strong)]"
                    }`}
                    aria-pressed={isHighContrast}
                    aria-label="High contrast theme"
                  >
                    <div className="w-12 h-12 mx-auto mb-3 rounded-lg bg-black border-2 border-white flex items-center justify-center shadow-sm">
                      <Contrast className="w-6 h-6 text-yellow-400" aria-hidden="true" />
                    </div>
                    <div className="text-sm font-medium text-center text-[var(--foreground)]">
                      Contrast
                    </div>
                    {isHighContrast && (
                      <div className="absolute top-2 right-2 w-5 h-5 bg-[#000080] rounded-full flex items-center justify-center">
                        <Check className="w-3 h-3 text-white" />
                      </div>
                    )}
                  </button>
                </div>
              </div>

              <Separator className="bg-[var(--border)]" />

              {/* Font Size */}
              <div className="space-y-4" role="group" aria-labelledby="font-size-label">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Type className="w-5 h-5 text-[var(--muted-foreground)]" aria-hidden="true" />
                    <div>
                      <Label id="font-size-label" className="text-base font-semibold text-[var(--foreground)]">
                        Text Size
                      </Label>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        Adjust for readability
                      </p>
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-[#000080] min-w-[4rem] text-right">
                    {fontSize}%
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => setFontSize(Math.max(75, fontSize - 12.5))}
                    disabled={fontSize <= 75}
                    aria-label="Decrease font size"
                    className="border-[var(--border)] text-[var(--foreground)]"
                  >
                    <Minus className="w-4 h-4" />
                  </Button>
                  <div className="flex-1">
                    <Slider
                      value={[fontSize]}
                      onValueChange={([value]) => setFontSize(value)}
                      min={75}
                      max={200}
                      step={12.5}
                      className="w-full"
                      aria-label="Font size slider"
                    />
                    <div className="flex justify-between text-xs text-[var(--muted-foreground)] mt-2">
                      <span>Small</span>
                      <span>Normal</span>
                      <span>Large</span>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => setFontSize(Math.min(200, fontSize + 12.5))}
                    disabled={fontSize >= 200}
                    aria-label="Increase font size"
                    className="border-[var(--border)] text-[var(--foreground)]"
                  >
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <Separator className="bg-[var(--border)]" />

              {/* Language */}
              <div className="space-y-4" role="group" aria-labelledby="language-label">
                <div className="flex items-center gap-3">
                  <Globe className="w-5 h-5 text-[var(--muted-foreground)]" aria-hidden="true" />
                  <div className="flex-1">
                    <Label id="language-label" className="text-base font-semibold text-[var(--foreground)]">
                      Language
                    </Label>
                    <p className="text-sm text-[var(--muted-foreground)]">
                      Select your preferred language
                    </p>
                  </div>
                </div>
                <Select value={language} onValueChange={setLanguage}>
                  <SelectTrigger className="h-12 bg-[var(--input-background)] border-[var(--border)] text-[var(--foreground)]" aria-label="Select language">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="hi">हिन्दी (Hindi)</SelectItem>
                    <SelectItem value="ta">தமிழ் (Tamil)</SelectItem>
                    <SelectItem value="te">తెలుగు (Telugu)</SelectItem>
                    <SelectItem value="bn">বাংলা (Bengali)</SelectItem>
                    <SelectItem value="mr">मराठी (Marathi)</SelectItem>
                    <SelectItem value="gu">ગુજરાતી (Gujarati)</SelectItem>
                    <SelectItem value="kn">ಕನ್ನಡ (Kannada)</SelectItem>
                    <SelectItem value="ml">മലയാളം (Malayalam)</SelectItem>
                    <SelectItem value="pa">ਪੰਜਾਬੀ (Punjabi)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Separator className="bg-[var(--border)]" />

              {/* Additional Options */}
              <div className="space-y-4">
                <h3 className="text-base font-semibold text-[var(--foreground)]">
                  Accessibility Options
                </h3>

                <div className="space-y-3">
                  <div className="flex items-center justify-between p-4 rounded-[var(--radius-lg)] bg-[var(--muted)]/30 hover:bg-[var(--muted)]/50 transition-colors">
                    <div className="flex-1">
                      <Label htmlFor="reduced-motion" className="cursor-pointer text-[var(--foreground)]">
                        Reduce Motion
                      </Label>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        Minimize animations
                      </p>
                    </div>
                    <Switch
                      id="reduced-motion"
                      checked={reducedMotion}
                      onCheckedChange={setReducedMotion}
                      aria-label="Toggle reduced motion"
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 rounded-[var(--radius-lg)] bg-[var(--muted)]/30 hover:bg-[var(--muted)]/50 transition-colors">
                    <div className="flex-1">
                      <Label htmlFor="screen-reader" className="cursor-pointer text-[var(--foreground)]">
                        Screen Reader
                      </Label>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        Enable announcements
                      </p>
                    </div>
                    <Switch
                      id="screen-reader"
                      checked={screenReaderAnnouncements}
                      onCheckedChange={setScreenReaderAnnouncements}
                      aria-label="Toggle screen reader announcements"
                    />
                  </div>
                </div>
              </div>

              <Separator className="bg-[var(--border)]" />

              {/* Help Tips */}
              <div className="space-y-3 p-4 rounded-[var(--radius-lg)] bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/20 border border-blue-200 dark:border-blue-900">
                <h4 className="font-semibold text-[var(--foreground)] flex items-center gap-2">
                  <Info className="w-4 h-4 text-blue-600" aria-hidden="true" />
                  Keyboard Shortcuts
                </h4>
                <ul className="space-y-2 text-sm text-[var(--foreground)]">
                  <li className="flex items-center gap-2">
                    <kbd className="px-2 py-1 bg-white dark:bg-gray-800 border border-[var(--border)] rounded text-xs font-mono">
                      Tab
                    </kbd>
                    <span className="text-[var(--muted-foreground)]">Navigate elements</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <kbd className="px-2 py-1 bg-white dark:bg-gray-800 border border-[var(--border)] rounded text-xs font-mono">
                      Esc
                    </kbd>
                    <span className="text-[var(--muted-foreground)]">Close dialogs</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <kbd className="px-2 py-1 bg-white dark:bg-gray-800 border border-[var(--border)] rounded text-xs font-mono">
                      Enter
                    </kbd>
                    <span className="text-[var(--muted-foreground)]">Activate buttons</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Footer */}
            <div className="sticky bottom-0 flex items-center justify-between p-6 bg-[var(--card)] border-t-2 border-[var(--border)] shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.1)]">
              <Button
                variant="outline"
                onClick={resetSettings}
                className="border-[var(--border)] text-[var(--foreground)]"
                aria-label="Reset all settings to default"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Reset
              </Button>
              <Button
                onClick={onClose}
                className="bg-[#000080] hover:bg-[#000066] text-white"
              >
                <Check className="w-4 h-4 mr-2" />
                Done
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
