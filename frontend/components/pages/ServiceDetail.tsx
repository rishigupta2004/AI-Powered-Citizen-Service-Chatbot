import React, { useState, useMemo, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import {
  ChevronRight,
  Download,
  FileText,
  ExternalLink,
  CheckCircle2,
  Clock,
  IndianRupee,
  Phone,
  Mail,
  MessageCircle,
  ArrowLeft,
  Calendar,
  Shield,
  Globe,
  HelpCircle,
} from 'lucide-react';
import { getServiceById, getAllServices } from '../../data/servicesData';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Separator } from '../ui/separator';
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '../ui/breadcrumb';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../ui/accordion';
import { API_BASE_URL } from '../../src/lib/api';
import { FormHelpModal } from '../FormHelpModal';

interface ServiceDetailProps {
  onNavigate: (page: string, serviceId?: string) => void;
  serviceId?: string;
}

export function ServiceDetail({ onNavigate, serviceId = 'passport_seva' }: ServiceDetailProps) {
  const { t, i18n } = useTranslation();
  const [activeStep, setActiveStep] = useState(1);
  // FormHelpModal state — null = closed, object = open with that doc's details
  const [helpDoc, setHelpDoc] = useState<{ name: string } | null>(null);
  const [expandedFAQ, setExpandedFAQ] = useState<string | null>('faq-0');
  const [liveDownloads, setLiveDownloads] = useState<Array<{ name: string; size: string; format: string; url?: string; source?: string }>>([]);

  const service = useMemo(() => getServiceById(serviceId) || getServiceById('passport_seva')!, [serviceId]);
  const allServices = useMemo(() => getAllServices(), []);
  const relatedServices = useMemo(
    () => allServices.filter((s) => s.category === service.category && s.id !== service.id).slice(0, 3),
    [allServices, service]
  );

  const ServiceIcon = service.icon;

  useEffect(() => {
    let cancelled = false;
    const loadDocs = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/service-docs/${service.id}`);
        const payload = await response.json();
        if (!cancelled && Array.isArray(payload?.documents)) {
          setLiveDownloads(payload.documents);
        }
      } catch {
        if (!cancelled) {
          setLiveDownloads([]);
        }
      }
    };
    loadDocs();
    return () => {
      cancelled = true;
    };
  }, [service.id]);

  const combinedDownloads = useMemo(() => {
    // Show live-fetched docs if available; otherwise fall back to static service.downloads
    const live = liveDownloads.length > 0 ? liveDownloads : [];
    // Merge live + static, deduplicate by name
    const allDocs = [...live];
    for (const d of service.downloads) {
      if (!allDocs.some((existing) => existing.name === d.name)) {
        allDocs.push(d);
      }
    }
    return allDocs;
  }, [liveDownloads, service.downloads]);

  return (
    <>
      <div className="min-h-screen bg-gradient-to-b from-[var(--background)] to-[var(--background-secondary)] pt-32 pb-20">
      <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)]">
        {/* Back Button */}
        <Button
          variant="ghost"
          onClick={() => onNavigate('services')}
          className="mb-6 -ml-2"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          {t('serviceDetail.backToServices', 'Back to Services')}
        </Button>

        {/* Breadcrumbs */}
        <Breadcrumb className="mb-8">
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink onClick={() => onNavigate('home')} className="cursor-pointer hover:text-[var(--primary)]">
                {t('navigation.home', 'Home')}
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbLink onClick={() => onNavigate('services')} className="cursor-pointer hover:text-[var(--primary)]">
                {t('navigation.services', 'Services')}
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>{service.name}</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-[var(--card)] rounded-[var(--radius-2xl)] shadow-[var(--shadow-8)] p-8 border-2 border-[var(--card-border)]"
            >
              <div className="flex items-start gap-6">
                <div className={`w-20 h-20 bg-gradient-to-br ${service.gradient} rounded-[var(--radius-2xl)] flex items-center justify-center shadow-[var(--shadow-8)] flex-shrink-0`}>
                  <ServiceIcon className="w-10 h-10 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3 flex-wrap">
                    <h1 className="text-3xl font-bold text-[var(--foreground)]">{service.name}</h1>
                    <Badge className="bg-[var(--accent)] text-white">{service.status}</Badge>
                  </div>
                  <p className="text-[var(--muted-foreground)] leading-relaxed mb-6">
                    {service.description}
                  </p>
                  <div className="flex flex-wrap gap-4">
                    <div className="flex items-center gap-2 text-sm text-[var(--muted-foreground)]">
                      <Clock className="w-4 h-4 text-[var(--primary)]" />
                      <span>{service.processingTime}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-[var(--muted-foreground)]">
                      <IndianRupee className="w-4 h-4 text-[var(--secondary)]" />
                      <span>{service.fee}</span>
                    </div>
                    {service.validity && (
                      <div className="flex items-center gap-2 text-sm text-[var(--muted-foreground)]">
                        <Calendar className="w-4 h-4 text-[var(--accent)]" />
                        <span>{t('serviceDetail.validityDuration', '{{value}} validity', { value: service.validity })}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-sm text-[var(--muted-foreground)]">
                      <Globe className="w-4 h-4 text-[var(--primary)]" />
                      <span>{service.mode}</span>
                    </div>
                  </div>
                  <a
                    href={service.officialUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-4 inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface-2)] px-3 py-1.5 text-xs font-medium text-[var(--color-navy)]"
                  >
                    {t('serviceDetail.officialSource', 'Official Source')}: {service.officialAuthority}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </motion.div>

            {/* Process Flow */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-[var(--card)] rounded-[var(--radius-2xl)] shadow-[var(--shadow-8)] p-8 border-2 border-[var(--card-border)]"
            >
              <h2 className="text-2xl font-bold text-[var(--foreground)] mb-6">{t('serviceDetail.applicationProcess', 'Application Process')}</h2>
              
              {/* Visual Stepper */}
              <div className="mb-8 bg-gradient-to-r from-[var(--muted)]/30 to-[var(--background-secondary)]/30 rounded-[var(--radius-xl)] p-6 border border-[var(--border)]">
                <div className="flex items-center justify-between relative">
                  {service.steps.map((step, index) => (
                    <React.Fragment key={step.number}>
                      <div className="flex flex-col items-center flex-1 relative z-10">
                        <div
                          className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold shadow-[var(--shadow-4)] transition-all ${
                            step.number <= activeStep
                              ? 'bg-[var(--accent)]'
                              : 'bg-[var(--muted)]'
                          }`}
                        >
                          {step.number <= activeStep ? (
                            <CheckCircle2 className="w-6 h-6" />
                          ) : (
                            step.number
                          )}
                        </div>
                        <div className="mt-3 text-center">
                          <div className="text-xs font-semibold text-[var(--muted-foreground)] uppercase">
                            {t('serviceDetail.step', 'Step {{number}}', { number: step.number })}
                          </div>
                        </div>
                      </div>
                      {index < service.steps.length - 1 && (
                        <div className="flex-1 h-1 bg-[var(--border)] -mx-4 relative" style={{ top: '-1.5rem' }}>
                          <div
                            className={`h-full transition-all ${
                              step.number < activeStep ? 'bg-[var(--accent)]' : 'bg-[var(--border)]'
                            }`}
                            style={{ width: step.number < activeStep ? '100%' : '0%' }}
                          />
                        </div>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>

              {/* Detailed Steps */}
              <div className="space-y-4">
                {service.steps.map((step) => (
                  <div
                    key={step.number}
                    className={`border-l-4 p-4 rounded-r-[var(--radius-lg)] transition-all ${
                      step.number <= activeStep
                        ? 'border-[var(--accent)] bg-[var(--success-bg)]'
                        : 'border-[var(--border)] bg-[var(--muted)]/20'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-[var(--foreground)] mb-1">{step.title}</h3>
                        <p className="text-sm text-[var(--muted-foreground)]">{step.description}</p>
                      </div>
                      {step.number <= activeStep && (
                        <CheckCircle2 className="w-5 h-5 text-[var(--accent)] flex-shrink-0" />
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 pt-6 border-t border-[var(--border)]">
                <Button
                  size="lg"
                  className="w-full bg-[var(--primary)] hover:bg-[var(--primary-hover)] shadow-[var(--shadow-4)] hover:shadow-[var(--shadow-8)] transition-all"
                  onClick={() => {
                    if (activeStep < service.steps.length) {
                      setActiveStep(activeStep + 1);
                    } else {
                      onNavigate('apply', service.id);
                    }
                  }}
                >
                  {activeStep < service.steps.length
                    ? t('serviceDetail.continueStep', 'Continue to Next Step')
                    : t('serviceDetail.startApplication', 'Start Application')}
                  <ChevronRight className="ml-2 w-5 h-5" />
                </Button>
              </div>
            </motion.div>

            {/* Required Documents */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-[var(--card)] rounded-[var(--radius-2xl)] shadow-[var(--shadow-8)] p-8 border-2 border-[var(--card-border)]"
            >
              <div className="flex items-center gap-3 mb-6">
                <Shield className="w-6 h-6 text-[var(--primary)]" />
                <h2 className="text-2xl font-bold text-[var(--foreground)]">{t('serviceDetail.requiredDocuments', 'Required Documents')}</h2>
              </div>
              <div className="space-y-3">
                {service.documents.map((doc, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-3 p-4 bg-[var(--muted)]/30 rounded-[var(--radius-lg)] border border-[var(--border)]"
                  >
                    <CheckCircle2 className={`w-5 h-5 ${doc.required ? 'text-[var(--accent)]' : 'text-[var(--muted-foreground)]'}`} />
                    <span className="flex-1 text-[var(--foreground)]">{doc.name}</span>
                    <Badge variant={doc.required ? 'default' : 'outline'} className={doc.required ? 'bg-[var(--accent)]' : ''}>
                      {doc.required ? t('common.required', 'Required') : t('common.optional', 'Optional')}
                    </Badge>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Downloads */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-[var(--card)] rounded-[var(--radius-2xl)] shadow-[var(--shadow-8)] p-8 border-2 border-[var(--card-border)]"
            >
              <h2 className="text-2xl font-bold text-[var(--foreground)] mb-6">{t('serviceDetail.downloadableResources', 'Downloadable Resources')}</h2>
              {combinedDownloads.length === 0 && (
                <div className="mb-4 rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--surface-2)] p-4 text-sm text-[var(--muted-foreground)]">
                  {t('serviceDetail.noOfficialPdf', 'No official PDF is available yet for this service. Please use the official portal.')}
                </div>
              )}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {combinedDownloads.map((doc, index) => {
                  const docHref = doc.url
                    ? (doc.url.startsWith('http') ? doc.url : `${API_BASE_URL}${doc.url}`)
                    : service.officialUrl;
                  return (
                  <div
                    key={index}
                    className="border-2 border-[var(--border)] rounded-[var(--radius-lg)] p-4 hover:border-[var(--primary)] hover:shadow-[var(--shadow-4)] transition-all cursor-pointer group"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-[var(--secondary)] to-[var(--secondary-hover)] rounded-[var(--radius-lg)] flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform shadow-[var(--shadow-2)]">
                        <FileText className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-[var(--foreground)] mb-1">{doc.name}</h4>
                        <div className="flex items-center gap-3 text-sm text-[var(--muted-foreground)] mb-3">
                          <span>{doc.size}</span>
                          <span>•</span>
                          <span>{doc.format}</span>
                        </div>
                        <div className="flex gap-2 flex-wrap">
                          <Button size="sm" variant="outline" className="border-[var(--primary)] text-[var(--primary)] hover:bg-[var(--primary)] hover:text-white" asChild>
                            <a href={docHref} target="_blank" rel="noreferrer" download>
                              <Download className="w-3 h-3 mr-1" />
                              {t('serviceDetail.download', 'Download')}
                            </a>
                          </Button>
                          <Button size="sm" variant="ghost" asChild>
                            <a href={docHref} target="_blank" rel="noreferrer" className="inline-flex items-center">
                              <ExternalLink className="w-3 h-3 mr-1" />
                              {t('common.view', 'View')}
                            </a>
                          </Button>
                          <Button
                             size="sm"
                             variant="ghost"
                             onClick={() => setHelpDoc({ name: doc.name })}
                             className="gap-1 text-[var(--accent)] hover:text-[var(--accent)] hover:bg-[var(--accent)]/10"
                             title={t('serviceDetail.helpButtonTitle', 'Why is this needed? How to fill it?')}
                           >
                             <HelpCircle className="w-3.5 h-3.5" />
                             {t('serviceDetail.helpButton', 'Help')}
                           </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                  );
                })}
              </div>
            </motion.div>

            {/* FAQ */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-[var(--card)] rounded-[var(--radius-2xl)] shadow-[var(--shadow-8)] p-8 border-2 border-[var(--card-border)]"
            >
              <h2 className="text-2xl font-bold text-[var(--foreground)] mb-6">{t('serviceDetail.faq', 'Frequently Asked Questions')}</h2>
              <Accordion type="single" collapsible value={expandedFAQ || undefined} onValueChange={setExpandedFAQ}>
                {service.faqs.map((faq, index) => (
                  <AccordionItem key={`faq-${index}`} value={`faq-${index}`} className="border-b border-[var(--border)]">
                    <AccordionTrigger className="text-left hover:no-underline py-4">
                      <div className="flex items-start gap-3 flex-1 pr-4">
                       <span className="text-sm font-semibold text-[var(--secondary)]">{t('serviceDetail.questionLabel', 'Q{{number}}:', { number: index + 1 })}</span>
                        <span className="font-semibold text-[var(--foreground)]">{faq.question}</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pl-8 pr-4 pb-4 text-[var(--muted-foreground)]">
                       <span className="text-sm font-semibold text-[var(--accent)] mr-2">{t('serviceDetail.answerLabel', 'A:')}</span>
                       {faq.answer}
                     </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </motion.div>

            {/* Related Services */}
            {relatedServices.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="bg-gradient-to-r from-[var(--muted)]/30 to-[var(--background-secondary)]/30 rounded-[var(--radius-2xl)] shadow-[var(--shadow-8)] p-8 border-2 border-[var(--border)]"
              >
                <h2 className="text-2xl font-bold text-[var(--foreground)] mb-6">{t('serviceDetail.relatedServices', 'Related Services')}</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {relatedServices.map((relatedService) => {
                    const RelatedIcon = relatedService.icon;
                    return (
                      <Card
                        key={relatedService.id}
                        className="cursor-pointer hover:shadow-[var(--shadow-8)] transition-all border-2 border-[var(--border)] hover:border-[var(--primary)] shadow-[var(--shadow-4)] group"
                        onClick={() => onNavigate('service-detail', relatedService.id)}
                      >
                        <CardHeader>
                          <div className={`w-12 h-12 bg-gradient-to-br ${relatedService.gradient} rounded-[var(--radius-lg)] flex items-center justify-center mb-3 group-hover:scale-110 transition-transform shadow-[var(--shadow-4)]`}>
                            <RelatedIcon className="w-6 h-6 text-white" />
                          </div>
                          <CardTitle className="text-base group-hover:text-[var(--primary)] transition-colors">{relatedService.name}</CardTitle>
                        </CardHeader>
                      </Card>
                    );
                  })}
                </div>
              </motion.div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Info */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-[var(--card)] rounded-[var(--radius-2xl)] shadow-[var(--shadow-8)] p-6 border-2 border-[var(--card-border)] sticky top-32"
            >
              <h3 className="font-bold text-[var(--foreground)] mb-4">{t('serviceDetail.serviceDetails', 'Service Details')}</h3>
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-[var(--muted-foreground)] mb-1">{t('serviceDetail.processingTime', 'Processing Time')}</div>
                  <div className="font-semibold text-[var(--foreground)]">{service.processingTime}</div>
                </div>
                <Separator />
                <div>
                  <div className="text-sm text-[var(--muted-foreground)] mb-1">{t('serviceDetail.applicationFee', 'Application Fee')}</div>
                  <div className="font-semibold text-[var(--foreground)]">{service.fee}</div>
                </div>
                <Separator />
                {service.validity && (
                  <>
                    <div>
                      <div className="text-sm text-[var(--muted-foreground)] mb-1">{t('serviceDetail.validity', 'Validity')}</div>
                      <div className="font-semibold text-[var(--foreground)]">{service.validity}</div>
                    </div>
                    <Separator />
                  </>
                )}
                <div>
                  <div className="text-sm text-[var(--muted-foreground)] mb-1">{t('serviceDetail.status', 'Status')}</div>
                  <Badge className="bg-[var(--accent)] text-white">{service.status}</Badge>
                </div>
              </div>
            </motion.div>

            {/* Contact Help */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-gradient-to-br from-[var(--primary)] to-[var(--primary-hover)] rounded-[var(--radius-2xl)] shadow-[var(--shadow-8)] p-6 text-white"
            >
              <h3 className="font-bold mb-4">{t('serviceDetail.needHelp', 'Need Help?')}</h3>
              <div className="space-y-3">
                <a href="tel:1800" className="flex items-center gap-3 p-3 bg-white/10 rounded-[var(--radius-lg)] hover:bg-white/20 transition-colors backdrop-blur-sm">
                  <Phone className="w-5 h-5" />
                  <div>
                    <div className="text-sm">{t('serviceDetail.tollFree', 'Toll-Free')}</div>
                    <div className="font-semibold">1800-XXX-XXXX</div>
                  </div>
                </a>
                <a href="mailto:" className="flex items-center gap-3 p-3 bg-white/10 rounded-[var(--radius-lg)] hover:bg-white/20 transition-colors backdrop-blur-sm">
                  <Mail className="w-5 h-5" />
                  <div>
                    <div className="text-sm">{t('serviceDetail.emailSupport', 'Email Support')}</div>
                    <div className="font-semibold text-xs">support@gov.in</div>
                  </div>
                </a>
              </div>
            </motion.div>

            {/* Chat Widget */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-gradient-to-br from-[var(--secondary)] to-[var(--secondary-hover)] rounded-[var(--radius-2xl)] shadow-[var(--shadow-8)] p-6 text-white text-center"
            >
              <MessageCircle className="w-12 h-12 mx-auto mb-3" />
              <h3 className="font-bold mb-2">{t('serviceDetail.liveChatSupport', 'Live Chat Support')}</h3>
              <p className="text-sm mb-4 text-white/90">{t('serviceDetail.instantHelp', 'Get instant help from our support team')}</p>
              <Button
                className="w-full bg-[var(--card)] text-[var(--color-navy)] hover:bg-[var(--surface-2)] shadow-[var(--shadow-4)]"
                onClick={() => {
                  window.dispatchEvent(
                    new CustomEvent('seva:open-chat', {
                      detail: {
                        message: `${service.name}: ${t('serviceDetail.instantHelp', 'Get instant help from our support team')}`,
                      },
                    })
                  );
                }}
              >
                {t('serviceDetail.startChat', 'Start Chat')}
              </Button>
            </motion.div>
          </div>
        </div>
      </div>
    </div>

    {/* FormHelpModal — rendered outside the main layout so it overlays everything cleanly */}
    <FormHelpModal
      isOpen={helpDoc !== null}
      onClose={() => setHelpDoc(null)}
      serviceId={serviceId}
      serviceName={service.name}
      documentName={helpDoc?.name ?? ''}
      initialLanguage={i18n.language?.split('-')[0] || 'en'}
    />
    </>
  );
}
