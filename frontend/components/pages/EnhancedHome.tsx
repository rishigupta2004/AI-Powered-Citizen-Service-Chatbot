import React, { useMemo, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { useTranslation } from "react-i18next";
import { ArrowRight, Bell, Clock3, FileText, Globe, LifeBuoy, Phone, Search, Shield, Siren, User } from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { ServiceCard3D } from "../3d/ServiceCard3D";
import { getAllServices } from "../../data/servicesData";

interface EnhancedHomeProps {
  onNavigate: (page: string, serviceId?: string) => void;
}

export function EnhancedHome({ onNavigate }: EnhancedHomeProps) {
  const { t } = useTranslation();
  const shouldReduceMotion = useReducedMotion();
  const [searchQuery, setSearchQuery] = useState("");

  const allServices = getAllServices();
  const quickAccessServices = allServices.slice(0, 6);
  const featuredServices = allServices.slice(0, 6);

  const searchResults = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return [];
    return allServices
      .filter((service) => service.name.toLowerCase().includes(query) || service.description.toLowerCase().includes(query))
      .slice(0, 4);
  }, [allServices, searchQuery]);

  const announcements = [
    t("home.ann1", "Income Certificate service maintenance window this Sunday 02:00-04:00 AM."),
    t("home.ann2", "Scholarship verification cycle is now open across all districts."),
    t("home.ann3", "Faster tracking notifications are now enabled for high-volume services."),
  ];

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();
    if (searchQuery.trim()) onNavigate("services");
  };

  return (
    <div className="page-shell min-h-screen pt-24 md:pt-28">
      <section className="border-b border-[var(--border)] bg-gradient-to-br from-[#051739] via-[#0a2f73] to-[#04112b] text-white">
        <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8 md:py-16">
          <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:gap-10">
            <motion.div
              initial={shouldReduceMotion ? false : { opacity: 0, y: 14 }}
              animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
              transition={{ duration: shouldReduceMotion ? 0 : 0.35 }}
            >
              <p className="page-eyebrow mb-4 border-white/35 bg-white/10 text-white">
                {t("home.hero.badge", "National Digital Citizen Platform")}
              </p>
              <h1 className="max-w-3xl text-balance text-4xl font-bold leading-tight tracking-[-0.03em] sm:text-5xl lg:text-6xl">
                {t("home.hero.title", "Your gateway to government services")}
              </h1>
              <p className="mt-4 max-w-2xl text-base leading-relaxed text-white/85 sm:text-lg">
                {t(
                  "home.hero.subtitle",
                  "Search, apply, and track government services from one secure platform designed for every citizen.",
                )}
              </p>

              <form onSubmit={handleSearch} className="glass-panel mt-7 rounded-[var(--radius-xl)] p-2.5">
                <div className="relative flex flex-col gap-2 sm:flex-row">
                  <Search className="pointer-events-none absolute left-4 top-1/2 h-4.5 w-4.5 -translate-y-1/2 text-white/60" />
                  <Input
                    type="text"
                    value={searchQuery}
                    onChange={(event) => setSearchQuery(event.target.value)}
                    placeholder={t("home.searchPlaceholder", "Search Passport, Income Certificate, Driving License...")}
                    className="h-12 border-0 bg-transparent pl-11 text-base text-white placeholder:text-white/55 shadow-none focus-visible:ring-0"
                  />
                  <Button type="submit" className="h-12 rounded-[var(--radius-lg)] bg-white px-6 text-[var(--color-navy)] hover:bg-white/90">
                    {t("home.searchCta", "Search Services")}
                  </Button>
                </div>

                {searchResults.length > 0 && (
                  <div className="mt-3 grid gap-2 sm:grid-cols-2">
                    {searchResults.map((service) => (
                      <button
                        key={service.id}
                        type="button"
                        onClick={() => onNavigate("service-detail", service.id)}
                        className="rounded-[var(--radius-md)] border border-white/20 bg-white/10 p-3 text-left transition-colors hover:bg-white/15"
                      >
                        <div className="truncate text-sm font-semibold text-white">{service.name}</div>
                        <div className="mt-1 truncate text-xs text-white/70">{service.processingTime}</div>
                      </button>
                    ))}
                  </div>
                )}
              </form>

              <div className="mt-4 flex flex-wrap gap-2">
                {[Globe, Shield, LifeBuoy, Bell].map((Icon, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={
                      index === 3
                        ? () => onNavigate("faq")
                        : index === 2
                          ? () =>
                              window.dispatchEvent(
                                new CustomEvent("seva:open-chat", {
                                  detail: {
                                    message: t("chatbot.welcome", "Namaste! Welcome to Seva Sindhu AI Assistant 🇮🇳"),
                                  },
                                }),
                              )
                          : undefined
                    }
                    className="inline-flex items-center gap-2 rounded-[var(--radius-md)] border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-white/90 transition-colors hover:bg-white/15"
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {index === 0
                      ? t("common.language", "Language")
                      : index === 1
                        ? t("common.accessibility", "Accessibility")
                        : index === 2
                          ? t("common.chat", "Live Chat")
                          : t("common.help", "Help")}
                  </button>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={shouldReduceMotion ? false : { opacity: 0, y: 20 }}
              animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
              transition={{ duration: shouldReduceMotion ? 0 : 0.4, delay: shouldReduceMotion ? 0 : 0.05 }}
              className="glass-panel rounded-[var(--radius-xl)] p-6"
            >
              <div className="text-xs font-semibold uppercase tracking-[0.08em] text-white/80">
                {t("home.glance", "Today at a glance")}
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3">
                {[
                  { label: t("home.stats.services", "Total Services"), value: "50+" },
                  { label: t("home.stats.languages", "Languages"), value: "22" },
                  { label: t("home.stats.uptime", "Platform Uptime"), value: "99.9%" },
                  { label: t("home.stats.support", "Citizen Support"), value: "24/7" },
                ].map((stat) => (
                  <div key={stat.label} className="rounded-[var(--radius-lg)] border border-white/20 bg-white/10 p-3">
                    <div className="text-2xl font-bold">{stat.value}</div>
                    <div className="mt-1 text-xs text-white/75">{stat.label}</div>
                  </div>
                ))}
              </div>
              <Button onClick={() => onNavigate("dashboard")} className="mt-5 h-11 w-full rounded-[var(--radius-lg)] bg-white text-[var(--color-navy)] hover:bg-white/90">
                {t("home.openDashboard", "Open Citizen Dashboard")}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </motion.div>
          </div>
        </div>
      </section>

      <section className="border-b border-[var(--border)] bg-[var(--surface-2)] py-12 md:py-14">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold tracking-[-0.01em] text-[var(--foreground)] md:text-3xl">{t("home.quickTitle", "Quick Access Services")}</h2>
          <p className="mt-1.5 text-sm text-[var(--muted-foreground)] md:text-base">{t("home.quickSubtitle", "Start common requests in one tap.")}</p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {quickAccessServices.map((service, index) => (
              <motion.button
                key={service.id}
                type="button"
                initial={shouldReduceMotion ? false : { opacity: 0, y: 10 }}
                whileInView={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-120px" }}
                transition={{ duration: shouldReduceMotion ? 0 : 0.2, delay: shouldReduceMotion ? 0 : index * 0.04 }}
                onClick={() => onNavigate("service-detail", service.id)}
                className="card-premium rounded-[var(--radius-xl)] p-5 text-left"
              >
                <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--muted-foreground)]">{service.processingTime}</p>
                <h3 className="mt-2 text-lg font-semibold text-[var(--foreground)]">{service.name}</h3>
                <p className="mt-1 line-clamp-2 text-sm text-[var(--muted-foreground)]">{service.description}</p>
                <span className="mt-3 inline-flex items-center text-sm font-medium text-[var(--color-navy)]">
                  {t("home.openService", "Open service")}
                  <ArrowRight className="ml-1.5 h-4 w-4" />
                </span>
              </motion.button>
            ))}
          </div>
        </div>
      </section>

      <section className="border-b border-[var(--border)] bg-[var(--surface-1)] py-12 md:py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold tracking-[-0.01em] text-[var(--foreground)] md:text-3xl">{t("home.popularTitle", "Popular Government Services")}</h2>
          <p className="mt-1.5 text-sm text-[var(--muted-foreground)] md:text-base">{t("home.popularSubtitle", "Most-used services by citizens this week.")}</p>

          <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {featuredServices.map((service, index) => (
              <motion.div
                key={service.id}
                initial={shouldReduceMotion ? false : { opacity: 0, y: 12 }}
                whileInView={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-90px" }}
                transition={{ duration: shouldReduceMotion ? 0 : 0.24, delay: shouldReduceMotion ? 0 : index * 0.05 }}
              >
                <ServiceCard3D
                  icon={service.icon}
                  name={service.name}
                  description={service.description}
                  badge={service.badge}
                  gradient={service.gradient}
                  processingTime={service.processingTime}
                  fee={service.fee}
                  onClick={() => onNavigate("service-detail", service.id)}
                />
              </motion.div>
            ))}
          </div>

          <div className="mt-10 text-center">
            <Button size="lg" className="cta-primary h-12 rounded-[var(--radius-lg)] px-8" onClick={() => onNavigate("services")}>
              {t("home.viewAll", "View All Services")}
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>
        </div>
      </section>

      <section className="border-b border-[var(--border)] bg-[var(--surface-2)] py-12 md:py-16">
        <div className="mx-auto grid max-w-7xl gap-6 px-4 sm:px-6 lg:grid-cols-[1.25fr_0.75fr] lg:px-8">
          <div className="rounded-[var(--radius-2xl)] border border-[var(--border)] bg-[var(--surface-1)] p-6 shadow-[var(--shadow-2)] md:p-8">
            <div className="flex items-center gap-2 text-sm text-[var(--muted-foreground)]">
              <User className="h-4 w-4" />
              {t("home.dashboardPreview", "Citizen Dashboard Preview")}
            </div>
            <h2 className="mt-3 text-2xl font-bold text-[var(--foreground)] md:text-3xl">{t("home.trackTitle", "Track every application in one place")}</h2>

            <div className="mt-6 grid gap-4 sm:grid-cols-3">
              {[
                { label: t("home.inProgress", "In Progress"), value: "03" },
                { label: t("home.approved", "Approved"), value: "08" },
                { label: t("home.actionRequired", "Action Required"), value: "01" },
              ].map((item, index) => (
                <div key={item.label} className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--surface-2)] p-4">
                  <div className={`text-2xl font-bold ${index === 2 ? "text-[#c86518]" : "text-[var(--color-navy)]"}`}>{item.value}</div>
                  <div className="mt-1 text-xs text-[var(--muted-foreground)]">{item.label}</div>
                </div>
              ))}
            </div>

            <div className="mt-6 space-y-3">
              {[
                t("home.activity1", "Passport renewal moved to document verification"),
                t("home.activity2", "Income certificate approved and ready for download"),
                t("home.activity3", "Scholarship form requires one additional upload"),
              ].map((item) => (
                <div key={item} className="flex items-start gap-3 rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--surface-2)] p-3">
                  <Clock3 className="mt-0.5 h-4 w-4 text-[var(--color-navy)]" />
                  <p className="text-sm text-[var(--foreground)]">{item}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              <Button onClick={() => onNavigate("dashboard")} className="cta-primary">{t("home.openDashboardShort", "Open Dashboard")}</Button>
              <Button variant="outline" className="cta-secondary" onClick={() => onNavigate("tracker")}>{t("home.trackStatus", "Track Status")}</Button>
            </div>
          </div>

          <div className="rounded-[var(--radius-2xl)] border border-[var(--border)] bg-[var(--surface-1)] p-6 shadow-[var(--shadow-2)]">
            <div className="flex items-center gap-2 text-sm text-[var(--muted-foreground)]">
              <Bell className="h-4 w-4" />
              {t("home.announcementsTitle", "Announcements & Latest Updates")}
            </div>
            <div className="mt-4 space-y-3">
              {announcements.map((item) => (
                <div key={item} className="rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--surface-2)] p-4">
                  <p className="text-sm text-[var(--foreground)]">{item}</p>
                </div>
              ))}
            </div>

            <Button variant="ghost" className="mt-4 h-auto px-0 text-[var(--color-navy)] hover:bg-transparent" onClick={() => onNavigate("faq")}>
              {t("home.learnMore", "Learn more updates")}
              <ArrowRight className="ml-1.5 h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>

      <section className="bg-[var(--surface-1)] py-12 md:py-14">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="rounded-[var(--radius-2xl)] border border-[#efc9c9] bg-[#fff9f9] p-6 shadow-[var(--shadow-2)] md:p-8">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <div className="inline-flex items-center gap-2 text-sm font-semibold text-red-700">
                  <Siren className="h-4 w-4" />
                  {t("home.emergencyTitle", "Emergency Services")}
                </div>
                <h3 className="mt-2 text-2xl font-bold text-[var(--foreground)] md:text-3xl">{t("home.emergencySub", "Immediate help and critical citizen support")}</h3>
                <p className="mt-2 max-w-3xl text-sm text-[var(--muted-foreground)] md:text-base">
                  {t(
                    "home.emergencyDesc",
                    "Use emergency channels for urgent police, ambulance, and fire services. For non-urgent requests, use standard portal workflows.",
                  )}
                </p>
              </div>

              <div className="grid w-full gap-3 sm:grid-cols-3 lg:w-auto">
                {[
                  { label: t("home.police", "Police"), value: "100" },
                  { label: t("home.ambulance", "Ambulance"), value: "108" },
                  { label: t("home.fire", "Fire"), value: "101" },
                ].map((item) => (
                  <div key={item.label} className="min-w-[112px] rounded-[var(--radius-md)] border border-[#efc9c9] bg-white px-4 py-3">
                    <div className="text-xs text-[var(--muted-foreground)]">{item.label}</div>
                    <div className="text-2xl font-bold text-red-700">{item.value}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              <Button className="bg-red-700 text-white hover:bg-red-600">
                <Phone className="mr-2 h-4 w-4" />
                {t("home.callEmergency", "Call Emergency")}
              </Button>
              <Button variant="outline" className="cta-secondary" onClick={() => onNavigate("about")}>
                <FileText className="mr-2 h-4 w-4" />
                {t("home.safetyGuide", "Safety Guidelines")}
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
