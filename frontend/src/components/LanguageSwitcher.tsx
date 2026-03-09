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
  const { i18n, t } = useTranslation();
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
          className="flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface-2)] text-[var(--foreground)] hover:bg-[var(--surface-3)] focus-visible:ring-2 focus-visible:ring-[var(--focus-ring-color)] outline-none transition-colors"
        >
          <Globe className="w-3.5 h-3.5" />
          <span className="hidden md:inline font-medium text-[11px]">{currentLanguage.nativeLabel}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        ref={menuRef}
        align="end"
        className="w-72 max-h-[420px] overflow-y-auto bg-[var(--surface-1)] border border-[var(--border)] shadow-[var(--shadow-12)] rounded-2xl p-0"
      >
        <div className="p-3 border-b border-[var(--border)] sticky top-0 bg-[var(--surface-1)]/95 backdrop-blur-md z-10">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--muted-foreground)]" />
            <input
              ref={searchInputRef}
              type="text"
              placeholder={t("navigation.searchLanguage", "Search languages...")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-sm bg-[var(--surface-2)] border border-[var(--border)] rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--focus-ring-color)] text-[var(--foreground)] placeholder:text-[var(--muted-foreground)] transition-all"
            />
          </div>
        </div>
        <div className="p-2" role="group">
          {groupedLanguages.map((group) => (
            <div key={group.script} className="mb-2 last:mb-0">
              <div className="px-3 py-1.5 text-[10px] font-bold text-[var(--muted-foreground)] uppercase tracking-widest">
                {group.script}
              </div>
              {group.languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => handleLanguageChange(lang.code)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 text-sm rounded-xl cursor-pointer transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring-color)] ${
                    i18n.language === lang.code 
                      ? "bg-[var(--surface-2)] text-[var(--color-navy)] font-semibold" 
                      : "text-[var(--foreground)] hover:bg-[var(--surface-2)]"
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <span>{lang.nativeLabel}</span>
                    <span className="text-[var(--muted-foreground)] text-xs font-normal">{lang.label}</span>
                  </span>
                  {i18n.language === lang.code && <Check className="w-4 h-4" />}
                </button>
              ))}
            </div>
          ))}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
