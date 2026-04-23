import React, { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { ExternalLink, HelpCircle, Search } from "lucide-react";
import { useTranslation } from "react-i18next";

import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Input } from "../ui/input";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "../ui/accordion";
import { getAllFaqItems } from "../../data/servicesData";

interface FAQPageProps {
  onNavigate: (page: string) => void;
}

export function FAQPage({ onNavigate }: FAQPageProps) {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  const allFaqs = useMemo(() => getAllFaqItems(), []);

  const categories = useMemo(() => {
    const counts = allFaqs.reduce<Record<string, number>>((acc, item) => {
      acc[item.category] = (acc[item.category] || 0) + 1;
      return acc;
    }, {});
    const sorted = Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([name, count]) => ({ id: name, name, count }));
    return [{ id: "all", name: t("faq.allQuestions", "All Questions"), count: allFaqs.length }, ...sorted];
  }, [allFaqs, t]);

  const filteredFaqs = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return allFaqs.filter((faq) => {
      const matchesCategory = selectedCategory === "all" || faq.category === selectedCategory;
      if (!matchesCategory) return false;
      if (!q) return true;
      return (
        faq.question.toLowerCase().includes(q) ||
        faq.answer.toLowerCase().includes(q) ||
        faq.serviceName.toLowerCase().includes(q)
      );
    });
  }, [allFaqs, searchQuery, selectedCategory]);

  return (
    <div className="page-shell min-h-screen pb-16 pt-24 md:pt-28">
      <section className="border-b border-[var(--border)] bg-gradient-to-br from-[#051739] via-[#0a2f73] to-[#04112b] text-white">
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 md:py-14">
          <div className="rounded-[var(--radius-2xl)] border border-white/20 bg-white/10 p-6 backdrop-blur-md md:p-8">
            <Badge className="mb-4 border-white/30 bg-white/15 text-white">{t("faq.verifiedDirectory", "Verified FAQ Directory")}</Badge>
            <h1 className="text-4xl font-bold tracking-[-0.03em] sm:text-5xl">{t("faq.serviceFaqs", "Service FAQs")}</h1>
            <p className="mt-3 max-w-3xl text-white/80">
              {t("faq.heroDescription", "Answers are generated from our verified national services catalog and mapped to official authorities.")}
            </p>
            <div className="mt-6 grid grid-cols-1 gap-3 md:grid-cols-3">
              <div className="rounded-lg border border-white/20 bg-white/10 px-4 py-3 text-sm">{t("faq.totalFaqs", "{{count}} total FAQs", { count: allFaqs.length })}</div>
              <div className="rounded-lg border border-white/20 bg-white/10 px-4 py-3 text-sm">{t("faq.categoryCount", "{{count}} categories", { count: categories.length - 1 })}</div>
              <div className="rounded-lg border border-white/20 bg-white/10 px-4 py-3 text-sm">{t("faq.sourcesLinked", "Sources linked per item")}</div>
            </div>
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <Card className="mt-6 border-[var(--border)] bg-[var(--surface-1)] shadow-[var(--shadow-4)]">
          <CardContent className="p-5 sm:p-6">
            <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
              <div className="relative md:col-span-2">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted-foreground)]" />
                <Input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t("faq.searchPlaceholder", "Search question, answer, or service")}
                  className="h-11 border-[var(--border)] bg-[var(--surface-1)] pl-9"
                />
              </div>
              <div className="flex items-center justify-end text-sm text-[var(--muted-foreground)]">
                {t("faq.showingCount", "Showing {{shown}} of {{total}}", {
                  shown: filteredFaqs.length,
                  total: allFaqs.length,
                })}
              </div>
            </div>
            <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`whitespace-nowrap rounded-full border px-3 py-1.5 text-xs transition ${
                    selectedCategory === category.id
                      ? "border-[var(--color-navy)] bg-[var(--color-navy)] text-white"
                      : "border-[var(--border)] bg-[var(--surface-2)] text-[var(--muted-foreground)]"
                  }`}
                >
                  {category.name} ({category.count})
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mt-6">
          <Card className="border-[var(--border)] bg-[var(--surface-1)] shadow-[var(--shadow-2)]">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <HelpCircle className="h-5 w-5" />
                {t("faq.verifiedAnswers", "Verified FAQ Answers")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Accordion type="single" collapsible className="w-full">
                {filteredFaqs.map((faq, index) => (
                  <AccordionItem key={`${faq.serviceId}-${index}`} value={`${faq.serviceId}-${index}`}>
                    <AccordionTrigger className="text-left">
                      <div className="pr-4">
                        <p className="font-semibold text-[var(--foreground)]">{faq.question}</p>
                        <p className="mt-1 text-xs text-[var(--muted-foreground)]">{faq.serviceName} • {faq.category}</p>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <p className="text-sm leading-relaxed text-[var(--muted-foreground)]">{faq.answer}</p>
                      <a
                        href={faq.officialUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-[var(--color-navy)]"
                      >
                        {t("faq.officialSource", "Official source")}: {faq.officialAuthority}
                        <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </CardContent>
          </Card>
        </motion.div>

        <div className="mt-8 flex justify-center">
          <Button variant="outline" onClick={() => onNavigate("services")}>{t("faq.exploreServices", "Explore services")}</Button>
        </div>
      </div>
    </div>
  );
}
