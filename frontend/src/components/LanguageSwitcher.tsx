import React, { useState, useMemo, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "../../components/ui/dropdown-menu";
import { Button } from "../../components/ui/button";
import { Globe, Check, Search } from "lucide-react";
import { supportedLanguages, changeLanguage } from "../i18n";

type Language = typeof supportedLanguages[number];

interface LanguageGroup {
  script: string;
  languages: Language[];
}

function groupLanguagesByScript(languages: Language[]): LanguageGroup[] {
  const groups: Record<string, Language[]> = {};
  
  for (const lang of languages) {
    if (!groups[lang.script]) {
      groups[lang.script] = [];
    }
    groups[lang.script].push(lang);
  }
  
  return Object.entries(groups)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([script, langs]) => ({ script, languages: langs }));
}

export function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const [search, setSearch] = useState("");
  const searchInputRef = useRef<HTMLInputElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  const currentLanguage = useMemo(
    () => supportedLanguages.find((lang) => lang.code === i18n.language) || supportedLanguages[0],
    [i18n.language]
  );

  const filteredLanguages = useMemo(() => {
    if (!search.trim()) return supportedLanguages;
    const query = search.toLowerCase();
    return supportedLanguages.filter(
      (lang) =>
        lang.label.toLowerCase().includes(query) ||
        lang.nativeLabel.toLowerCase().includes(query) ||
        lang.code.toLowerCase().includes(query)
    );
  }, [search]);

  const groupedLanguages = useMemo(
    () => groupLanguagesByScript(filteredLanguages),
    [filteredLanguages]
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setSearch("");
      }
    };
    const menu = menuRef.current;
    menu?.addEventListener("keydown", handleKeyDown);
    return () => {
      menu?.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  const handleLanguageChange = async (code: string) => {
    await changeLanguage(code);
    setSearch("");
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="flex items-center gap-2 text-[var(--foreground)] hover:text-[var(--foreground)] hover:bg-[var(--muted)]"
          aria-label={`Current language: ${currentLanguage.label}. Select language.`}
        >
          <Globe className="w-4 h-4" />
          <span className="hidden md:inline">{currentLanguage.nativeLabel}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        ref={menuRef}
        align="end"
        className="w-64 max-h-80 overflow-y-auto"
        onCloseAutoFocus={() => setSearch("")}
      >
        <div className="p-2 border-b border-[var(--border)]">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search languages..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-sm bg-background border border-input rounded-md focus:outline-none focus:ring-1 focus:ring-ring"
              aria-label="Search languages"
            />
          </div>
        </div>
        <div className="py-1" role="group" aria-label="Language groups">
          {groupedLanguages.map((group) => (
            <div key={group.script} className="mb-1">
              <div className="px-2 py-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                {group.script} ({group.languages.length})
              </div>
              {group.languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => handleLanguageChange(lang.code)}
                  className={`w-full flex items-center justify-between px-3 py-2 text-sm cursor-pointer hover:bg-[var(--muted)] focus:outline-none focus:bg-[var(--muted)] ${
                    i18n.language === lang.code ? "bg-[var(--muted)]" : ""
                  }`}
                  role="menuitem"
                  aria-selected={i18n.language === lang.code}
                >
                  <span className="flex items-center gap-2">
                    <span className="font-medium">{lang.nativeLabel}</span>
                    <span className="text-muted-foreground text-xs">{lang.label}</span>
                  </span>
                  {i18n.language === lang.code && (
                    <Check className="w-4 h-4 text-primary" />
                  )}
                </button>
              ))}
            </div>
          ))}
          {filteredLanguages.length === 0 && (
            <div className="px-3 py-4 text-sm text-center text-muted-foreground">
              No languages found
            </div>
          )}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
