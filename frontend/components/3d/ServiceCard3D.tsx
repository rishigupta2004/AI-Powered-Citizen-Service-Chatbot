import React, { useMemo } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { ArrowRight, Clock3, FileText, IndianRupee, LucideIcon } from "lucide-react";
import { useTranslation } from "react-i18next";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";

interface ServiceCard3DProps {
  icon: LucideIcon;
  name: string;
  description: string;
  badge: string;
  gradient: string;
  processingTime: string;
  fee: string;
  mode?: string;
  officialAuthority?: string;
  onClick?: () => void;
}

export function ServiceCard3D({
  icon: Icon,
  name,
  description,
  badge,
  gradient,
  processingTime,
  fee,
  mode,
  officialAuthority,
  onClick,
}: ServiceCard3DProps) {
  const { t } = useTranslation();
  const shouldReduceMotion = useReducedMotion();

  const documentCue = useMemo(() => {
    const signal = `${name} ${description} ${processingTime} ${fee}`.toLowerCase();
    if (signal.includes("same day") || signal.includes("instant")) return t("card.docsFew", "1-2 documents");
    if (signal.includes("certificate") || signal.includes("verification")) return t("card.docsMany", "3-5 documents");
    return t("card.docsChecklist", "Checklist after opening");
  }, [description, fee, name, processingTime, t]);

  const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (!onClick) return;
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onClick();
    }
  };

  return (
    <motion.div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      whileHover={shouldReduceMotion ? undefined : { y: -3 }}
      transition={shouldReduceMotion ? { duration: 0 } : { type: "spring", stiffness: 250, damping: 24 }}
      className="group card-premium cursor-pointer overflow-hidden rounded-[var(--radius-xl)]"
      aria-label={`${t("card.open", "Open")} ${name}`}
    >
      <div className="h-[2px] bg-gradient-to-r from-[#ff9933] via-[var(--color-navy)] to-[#138808]" />

      <div className="flex items-start justify-between gap-3 p-5">
        <div className="flex items-start gap-3">
          <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-[var(--radius-lg)] bg-gradient-to-br ${gradient} shadow-[var(--shadow-2)]`}>
            <Icon className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold tracking-[-0.01em] text-[var(--foreground)]">{name}</h3>
            <p className="mt-1.5 line-clamp-2 text-sm leading-relaxed text-[var(--muted-foreground)]">{description}</p>
          </div>
        </div>
        <Badge className="border-[var(--border)] bg-[var(--surface-2)] text-[var(--muted-foreground)]">{badge}</Badge>
      </div>

      <div className="grid grid-cols-1 gap-2.5 px-5 pb-4 sm:grid-cols-3">
        <div className="rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--surface-2)] px-3 py-2.5">
          <p className="mb-1 flex items-center gap-1 text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--muted-foreground)]">
            <Clock3 className="h-3 w-3" />
            {t("card.processing", "Processing")}
          </p>
          <p className="text-sm font-semibold text-[var(--foreground)]">{processingTime}</p>
        </div>

        <div className="rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--surface-2)] px-3 py-2.5">
          <p className="mb-1 flex items-center gap-1 text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--muted-foreground)]">
            <IndianRupee className="h-3 w-3" />
            {t("card.fee", "Fee")}
          </p>
          <p className="text-sm font-semibold text-[var(--foreground)]">{fee}</p>
        </div>

        <div className="rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--surface-2)] px-3 py-2.5">
          <p className="mb-1 flex items-center gap-1 text-[10px] font-semibold uppercase tracking-[0.08em] text-[var(--muted-foreground)]">
            <FileText className="h-3 w-3" />
            {t("card.documents", "Documents")}
          </p>
          <p className="text-sm font-semibold text-[var(--foreground)]">{documentCue}</p>
        </div>
      </div>

      <div className="px-5 pb-5">
        {(mode || officialAuthority) && (
          <div className="mb-3 rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--surface-2)] px-3 py-2 text-xs text-[var(--muted-foreground)]">
            {mode && <span className="font-semibold text-[var(--foreground)]">{mode}</span>}
            {mode && officialAuthority && <span> • </span>}
            {officialAuthority && <span className="line-clamp-1">{officialAuthority}</span>}
          </div>
        )}
        <Button className="cta-primary h-10 w-full rounded-[var(--radius-md)]">
          {t("card.viewDetails", "View Details")}
          <ArrowRight className="ml-2 h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5" />
        </Button>
      </div>
    </motion.div>
  );
}
