import React, { useMemo, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { useTranslation } from "react-i18next";
import {
  ArrowRight,
  Bell,
  CircleDashed,
  Clock,
  Filter,
  Grid3x3,
  IndianRupee,
  LifeBuoy,
  List,
  Search,
  ShieldCheck,
  X,
} from "lucide-react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Badge } from "../ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { ServiceCard3D } from "../3d/ServiceCard3D";
import { getAllServices } from "../../data/servicesData";

interface ServicesPageProps {
  onNavigate: (page: string, serviceId?: string) => void;
}

export function ServicesPage({ onNavigate }: ServicesPageProps) {
  const { t } = useTranslation();
  const shouldReduceMotion = useReducedMotion();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [statusReference, setStatusReference] = useState("");
  const [statusMessage, setStatusMessage] = useState(
    t("services.statusDefault", "Enter an application reference to view a sample status."),
  );
  const [statusError, setStatusError] = useState("");

  const allServices = useMemo(() => getAllServices(), []);

  const categories = useMemo(
    () => ["all", ...Array.from(new Set(allServices.map((service) => service.category)))],
    [allServices],
  );

  const categoryCountMap = useMemo(
    () =>
      allServices.reduce((acc, service) => {
        acc[service.category] = (acc[service.category] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
    [allServices],
  );

  const filteredServices = useMemo(
    () =>
      allServices.filter((service) => {
        const query = searchQuery.toLowerCase();
        const matchesSearch =
          service.name.toLowerCase().includes(query) ||
          service.description.toLowerCase().includes(query);
        const matchesCategory = selectedCategory === "all" || service.category === selectedCategory;
        return matchesSearch && matchesCategory;
      }),
    [allServices, searchQuery, selectedCategory],
  );

  const groupedServices = useMemo(
    () =>
      filteredServices.reduce((acc, service) => {
        if (!acc[service.category]) acc[service.category] = [];
        acc[service.category].push(service);
        return acc;
      }, {} as Record<string, typeof allServices>),
    [filteredServices, allServices],
  );

  const orderedGroups = useMemo(
    () =>
      Object.entries(groupedServices).sort((a, b) => {
        if (a[1].length !== b[1].length) return b[1].length - a[1].length;
        return a[0].localeCompare(b[0]);
      }),
    [groupedServices],
  );

  const referencePattern = /^[A-Za-z]{2,5}-\d{4}-\d{3,6}$/;

  const announcements = [
    t("services.announcement1", "Digital certificate workflow launched for faster approvals."),
    t("services.announcement2", "Scheduled maintenance: Sunday 1:00 AM to 3:00 AM."),
    t("services.announcement3", "Temporary outage alert for high-volume verification uploads."),
  ];

  const clearFilters = () => {
    setSearchQuery("");
    setSelectedCategory("all");
  };

  const handleStatusCheck = () => {
    const reference = statusReference.trim();

    if (!reference) {
      setStatusError("");
      setStatusMessage(t("services.statusDefault", "Enter an application reference to view a sample status."));
      return;
    }

    if (!referencePattern.test(reference)) {
      setStatusError(t("services.statusInvalid", "Invalid reference format. Use format: APP-2026-1482."));
      setStatusMessage(t("services.statusFix", "Please correct the reference and try again."));
      return;
    }

    setStatusError("");
    const inFinalStep = reference.length % 2 === 0;
    setStatusMessage(
      inFinalStep
        ? t("services.statusDone", "Application is in final verification and ready for download.")
        : t("services.statusReview", "Application is under review. Expected update within 2 business days."),
    );
  };

  return (
    <div className="page-shell min-h-screen pb-16 pt-24 md:pt-28">
      <section className="border-b border-[var(--border)] bg-gradient-to-br from-[#051739] via-[#0a2f73] to-[#04112b] text-white">
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 md:py-14">
          <div className="rounded-[var(--radius-2xl)] border border-white/20 bg-white/10 p-6 backdrop-blur-md md:p-8">
            <Badge className="mb-4 border-white/30 bg-white/15 text-white">
              {t("services.badge", "National Digital Services Catalogue")}
            </Badge>
            <h1 className="text-4xl font-bold tracking-[-0.03em] sm:text-5xl">
              {t("services.title", "All Government Services")}
            </h1>
            <p className="mt-3 max-w-3xl text-white/80">
              {t(
                "services.subtitle",
                "Discover and access verified services with transparent timelines, streamlined categories, and guided navigation.",
              )}
            </p>
            <div className="mt-6 flex flex-wrap gap-2">
              <Badge variant="outline" className="border-white/30 bg-white/10 text-white">
                {allServices.length} {t("services.services", "Services")}
              </Badge>
              <Badge variant="outline" className="border-white/30 bg-white/10 text-white">
                {categories.length - 1} {t("services.categoryLabel", "Categories")}
              </Badge>
              <Badge variant="outline" className="border-white/30 bg-white/10 text-white">
                <ShieldCheck className="mr-1.5 h-3.5 w-3.5" />
                {t("services.verified", "Verified and secure")}
              </Badge>
            </div>
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <Card className="mt-6 border-[var(--border)] bg-[var(--surface-1)] shadow-[var(--shadow-2)]">
          <CardContent className="p-4 sm:p-5">
            <div className="flex items-center gap-2 text-sm font-semibold text-[var(--color-navy)]">
              <Bell className="h-4 w-4" />
              {t("services.publicAnnouncements", "Public Announcements")}
            </div>
            <div className="mt-3 grid gap-2 md:grid-cols-3">
              {announcements.map((item) => (
                <div
                  key={item}
                  className="rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--surface-2)] px-3 py-2.5 text-xs text-[var(--muted-foreground)]"
                >
                  {item}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="mt-6 border-[var(--border)] bg-[var(--surface-1)] shadow-[var(--shadow-4)]">
          <CardContent className="p-5 sm:p-6">
            <div className="mb-5 flex flex-wrap items-start justify-between gap-3 border-b border-[var(--border)] pb-4">
              <div>
                <h2 className="text-lg font-semibold tracking-[-0.01em] text-[var(--foreground)]">
                  {t("services.toolbar", "Service Discovery Toolbar")}
                </h2>
                <p className="text-sm text-[var(--muted-foreground)]">
                  {t("services.toolbarSub", "Refine by name, category, and preferred layout.")}
                </p>
              </div>
              <div className="rounded-full border border-[var(--border)] bg-[var(--surface-2)] px-3 py-1 text-xs text-[var(--muted-foreground)]">
                {t("services.showing", "Showing")} {filteredServices.length} {t("services.of", "of")} {allServices.length}
                {searchQuery && ` ${t("services.for", "for")} "${searchQuery}"`}
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <div className="relative md:col-span-2">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--muted-foreground)]" />
                <Input
                  type="text"
                  placeholder={t("services.search", "Search by service name or purpose")}
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                  className="h-11 border-[var(--border)] bg-[var(--surface-1)] pl-9"
                />
                {searchQuery && (
                  <Button
                    type="button"
                    size="icon"
                    variant="ghost"
                    className="absolute right-1.5 top-1/2 h-8 w-8 -translate-y-1/2 hover:bg-[var(--surface-2)]"
                    onClick={() => setSearchQuery("")}
                    aria-label={t("services.clearSearch", "Clear search")}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>

              <div className="flex gap-2">
                <div className="flex-1">
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="h-11 border-[var(--border)] bg-[var(--surface-1)]">
                      <Filter className="mr-2 h-4 w-4" />
                      <SelectValue placeholder={t("services.category", "Category")} />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category === "all" ? t("services.allCategories", "All Categories") : category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--surface-1)]">
                  <Button
                    variant={viewMode === "grid" ? "default" : "ghost"}
                    size="sm"
                    className="h-11 rounded-r-none"
                    onClick={() => setViewMode("grid")}
                  >
                    <Grid3x3 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant={viewMode === "list" ? "default" : "ghost"}
                    size="sm"
                    className="h-11 rounded-l-none"
                    onClick={() => setViewMode("list")}
                  >
                    <List className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>

            <div className="mt-4 flex gap-2 overflow-x-auto pb-1">
              {categories.map((category) => {
                const isActive = selectedCategory === category;
                const count = category === "all" ? allServices.length : (categoryCountMap[category] || 0);
                return (
                  <Button
                    key={category}
                    variant={isActive ? "default" : "outline"}
                    size="sm"
                    className="whitespace-nowrap"
                    onClick={() => setSelectedCategory(category)}
                  >
                    {category === "all" ? t("services.allCategories", "All Categories") : category}
                    <Badge className={`ml-2 ${isActive ? "bg-white/20 text-white" : "bg-[var(--surface-2)] text-[var(--muted-foreground)]"}`}>
                      {count}
                    </Badge>
                  </Button>
                );
              })}
            </div>

            {(searchQuery || selectedCategory !== "all") && (
              <div className="mt-4 flex items-center justify-end">
                <Button variant="outline" size="sm" className="cta-secondary" onClick={clearFilters}>
                  {t("services.clearFilters", "Clear all filters")}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <motion.div
          initial={shouldReduceMotion ? false : { opacity: 0, y: 10 }}
          animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
          transition={{ delay: shouldReduceMotion ? 0 : 0.08, duration: shouldReduceMotion ? 0 : 0.2 }}
          className="mb-10 mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2"
        >
          <Card className="card-premium border-[var(--border)] bg-[var(--surface-1)]">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-lg">
                <CircleDashed className="h-5 w-5 text-[var(--color-navy)]" />
                {t("services.statusChecker", "Service Status Checker")}
              </CardTitle>
              <CardDescription>{t("services.statusCheckerSub", "Quick status preview for applicants and families.")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Input
                value={statusReference}
                onChange={(event) => setStatusReference(event.target.value)}
                placeholder={t("services.statusPlaceholder", "Enter reference ID (e.g., APP-2026-1482)")}
                className={`border-[var(--border)] ${statusError ? "border-[#b42318] focus-visible:ring-[#b42318]" : ""}`}
                aria-invalid={statusError ? true : undefined}
              />
              {statusError && <p className="text-xs font-medium text-[#a42720]">{statusError}</p>}
              <Button onClick={handleStatusCheck} className="cta-primary w-full">
                {t("services.checkStatus", "Check Status")}
              </Button>
              <p className="text-sm leading-relaxed text-[var(--muted-foreground)]">{statusMessage}</p>
            </CardContent>
          </Card>

          <Card className="card-premium border-[var(--border)] bg-[var(--surface-1)]">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-lg">
                <LifeBuoy className="h-5 w-5 text-[var(--color-navy)]" />
                {t("services.helpCenter", "Help Center")}
              </CardTitle>
              <CardDescription>{t("services.helpCenterSub", "Guidance for forms, documents, eligibility, and escalations.")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <Button variant="outline" className="cta-secondary" onClick={() => onNavigate("faq")}>
                  {t("services.visitFaq", "Visit FAQ")}
                </Button>
                <Button variant="outline" className="cta-secondary">{t("services.guidedSupport", "Guided Support")}</Button>
              </div>
              <div className="rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--surface-2)] p-3 text-sm text-[var(--muted-foreground)]">
                {t("services.responseTime", "Average response time: under 10 minutes during working hours.")}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {viewMode === "grid" ? (
          <>
            {orderedGroups.map(([category, services], categoryIndex) => (
              <motion.div
                key={category}
                initial={shouldReduceMotion ? false : { opacity: 0, y: 12 }}
                animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
                transition={{ delay: shouldReduceMotion ? 0 : 0.12 + categoryIndex * 0.04, duration: shouldReduceMotion ? 0 : 0.22 }}
                className="mb-12"
              >
                <div className="mb-5 rounded-[var(--radius-xl)] border border-[var(--border)] bg-[var(--surface-1)] p-4 sm:p-5">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h2 className="text-2xl font-bold text-[var(--foreground)] sm:text-3xl">{category}</h2>
                      <p className="mt-1 text-sm text-[var(--muted-foreground)]">
                        {t("services.groupSubtitle", "Streamlined services grouped for easier discovery.")}
                      </p>
                    </div>
                    <Badge variant="secondary" className="text-sm">{services.length}</Badge>
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {services.map((service, index) => (
                    <motion.div
                      key={service.id}
                      initial={shouldReduceMotion ? false : { opacity: 0, y: 10 }}
                      animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
                      transition={{ delay: shouldReduceMotion ? 0 : 0.16 + index * 0.02, duration: shouldReduceMotion ? 0 : 0.2 }}
                    >
                      <ServiceCard3D
                        icon={service.icon}
                        name={service.name}
                        description={service.description}
                        badge={service.badge}
                        gradient={service.gradient}
                        processingTime={service.processingTime}
                        fee={service.fee}
                        mode={service.mode}
                        officialAuthority={service.officialAuthority}
                        onClick={() => onNavigate("service-detail", service.id)}
                      />
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            ))}
          </>
        ) : (
          <div className="space-y-4">
            {filteredServices.map((service, index) => (
              <motion.div
                key={service.id}
                initial={shouldReduceMotion ? false : { opacity: 0, x: -10 }}
                animate={shouldReduceMotion ? undefined : { opacity: 1, x: 0 }}
                transition={{ delay: shouldReduceMotion ? 0 : index * 0.02, duration: shouldReduceMotion ? 0 : 0.2 }}
              >
                <Card
                  className="group cursor-pointer border-[var(--border)] bg-[var(--surface-1)] transition-all hover:-translate-y-[1px] hover:shadow-[var(--shadow-4)]"
                  onClick={() => onNavigate("service-detail", service.id)}
                >
                  <CardContent className="p-5 sm:p-6">
                    <div className="flex items-center gap-4 sm:gap-6">
                      <div className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-[var(--radius-lg)] bg-gradient-to-br ${service.gradient} shadow-[var(--shadow-2)]`}>
                        <service.icon className="h-7 w-7 text-white" />
                      </div>

                      <div className="min-w-0 flex-1">
                        <div className="mb-1.5 flex flex-wrap items-center gap-2">
                          <h3 className="text-lg font-semibold text-[var(--foreground)] sm:text-xl">{service.name}</h3>
                          {service.badge && <Badge variant="secondary">{service.badge}</Badge>}
                        </div>
                        <p className="mb-3 text-sm text-[var(--muted-foreground)]">{service.description}</p>
                        <div className="flex flex-wrap items-center gap-4 text-sm">
                          <div className="flex items-center gap-1 text-[var(--muted-foreground)]">
                            <Clock className="h-4 w-4" />
                            <span>{service.processingTime}</span>
                          </div>
                          <div className="flex items-center gap-1 text-[var(--muted-foreground)]">
                            <IndianRupee className="h-4 w-4" />
                            <span>{service.fee}</span>
                          </div>
                          <Badge variant="outline" className="text-xs">{service.category}</Badge>
                          <Badge variant="outline" className="text-xs">{service.mode}</Badge>
                        </div>
                        <a
                          href={service.officialUrl}
                          target="_blank"
                          rel="noreferrer"
                          className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-[var(--color-navy)]"
                          onClick={(e) => e.stopPropagation()}
                        >
                          Official: {service.officialAuthority}
                        </a>
                      </div>

                      <ArrowRight className="h-5 w-5 shrink-0 text-[var(--muted-foreground)] transition-transform group-hover:translate-x-0.5" />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}

        {filteredServices.length === 0 && (
          <motion.div
            initial={shouldReduceMotion ? false : { opacity: 0, scale: 0.985 }}
            animate={shouldReduceMotion ? undefined : { opacity: 1, scale: 1 }}
            className="py-16 text-center"
          >
            <div className="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-full bg-[var(--surface-2)]">
              <Search className="h-9 w-9 text-[var(--muted-foreground)]" />
            </div>
            <h3 className="mb-2 text-2xl font-semibold text-[var(--foreground)]">{t("services.noResults", "No services found")}</h3>
            <p className="mb-6 text-[var(--muted-foreground)]">{t("services.noResultsSub", "Try adjusting your search or filter criteria.")}</p>
            <Button variant="outline" className="cta-secondary" onClick={clearFilters}>
              {t("services.clearFilters", "Clear all filters")}
            </Button>
          </motion.div>
        )}
      </div>
    </div>
  );
}
