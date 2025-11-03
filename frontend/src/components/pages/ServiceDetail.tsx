import React, { useState, useMemo } from 'react';
import { motion } from 'motion/react';
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
} from 'lucide-react';
import { getServiceById, getAllServices } from '../../data/servicesData';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Separator } from '../ui/separator';
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator } from '../ui/breadcrumb';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../ui/accordion';

interface ServiceDetailProps {
  onNavigate: (page: string, serviceId?: string) => void;
  serviceId?: string;
}

export function ServiceDetail({ onNavigate, serviceId = 'passport' }: ServiceDetailProps) {
  const [activeStep, setActiveStep] = useState(1);
  const [expandedFAQ, setExpandedFAQ] = useState<string | null>('faq-0');

  const service = useMemo(() => getServiceById(serviceId) || getServiceById('passport')!, [serviceId]);
  const allServices = useMemo(() => getAllServices(), []);
  const relatedServices = useMemo(
    () => allServices.filter((s) => s.category === service.category && s.id !== service.id).slice(0, 3),
    [allServices, service]
  );

  const ServiceIcon = service.icon;

  return (
    <div className="min-h-screen bg-gradient-to-b from-[var(--background)] to-[var(--background-secondary)] pt-32 pb-20">
      <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)]">
        {/* Back Button */}
        <Button
          variant="ghost"
          onClick={() => onNavigate('services')}
          className="mb-6 -ml-2"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Services
        </Button>

        {/* Breadcrumbs */}
        <Breadcrumb className="mb-8">
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink onClick={() => onNavigate('home')} className="cursor-pointer hover:text-[var(--primary)]">
                Home
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbLink onClick={() => onNavigate('services')} className="cursor-pointer hover:text-[var(--primary)]">
                Services
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
                        <span>{service.validity} validity</span>
                      </div>
                    )}
                  </div>
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
              <h2 className="text-2xl font-bold text-[var(--foreground)] mb-6">Application Process</h2>
              
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
                            Step {step.number}
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
                    }
                  }}
                >
                  {activeStep < service.steps.length ? 'Continue to Next Step' : 'Start Application'}
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
                <h2 className="text-2xl font-bold text-[var(--foreground)]">Required Documents</h2>
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
                      {doc.required ? 'Required' : 'Optional'}
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
              <h2 className="text-2xl font-bold text-[var(--foreground)] mb-6">Downloadable Resources</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {service.downloads.map((doc, index) => (
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
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline" className="border-[var(--primary)] text-[var(--primary)] hover:bg-[var(--primary)] hover:text-white">
                            <Download className="w-3 h-3 mr-1" />
                            Download
                          </Button>
                          <Button size="sm" variant="ghost">
                            <ExternalLink className="w-3 h-3 mr-1" />
                            View
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* FAQ */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-[var(--card)] rounded-[var(--radius-2xl)] shadow-[var(--shadow-8)] p-8 border-2 border-[var(--card-border)]"
            >
              <h2 className="text-2xl font-bold text-[var(--foreground)] mb-6">Frequently Asked Questions</h2>
              <Accordion type="single" collapsible value={expandedFAQ || undefined} onValueChange={setExpandedFAQ}>
                {service.faqs.map((faq, index) => (
                  <AccordionItem key={`faq-${index}`} value={`faq-${index}`} className="border-b border-[var(--border)]">
                    <AccordionTrigger className="text-left hover:no-underline py-4">
                      <div className="flex items-start gap-3 flex-1 pr-4">
                        <span className="text-sm font-semibold text-[var(--secondary)]">Q{index + 1}:</span>
                        <span className="font-semibold text-[var(--foreground)]">{faq.question}</span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="pl-8 pr-4 pb-4 text-[var(--muted-foreground)]">
                      <span className="text-sm font-semibold text-[var(--accent)] mr-2">A:</span>
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
                <h2 className="text-2xl font-bold text-[var(--foreground)] mb-6">Related Services</h2>
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
              <h3 className="font-bold text-[var(--foreground)] mb-4">Service Details</h3>
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-[var(--muted-foreground)] mb-1">Processing Time</div>
                  <div className="font-semibold text-[var(--foreground)]">{service.processingTime}</div>
                </div>
                <Separator />
                <div>
                  <div className="text-sm text-[var(--muted-foreground)] mb-1">Application Fee</div>
                  <div className="font-semibold text-[var(--foreground)]">{service.fee}</div>
                </div>
                <Separator />
                {service.validity && (
                  <>
                    <div>
                      <div className="text-sm text-[var(--muted-foreground)] mb-1">Validity</div>
                      <div className="font-semibold text-[var(--foreground)]">{service.validity}</div>
                    </div>
                    <Separator />
                  </>
                )}
                <div>
                  <div className="text-sm text-[var(--muted-foreground)] mb-1">Status</div>
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
              <h3 className="font-bold mb-4">Need Help?</h3>
              <div className="space-y-3">
                <a href="tel:1800" className="flex items-center gap-3 p-3 bg-white/10 rounded-[var(--radius-lg)] hover:bg-white/20 transition-colors backdrop-blur-sm">
                  <Phone className="w-5 h-5" />
                  <div>
                    <div className="text-sm">Toll-Free</div>
                    <div className="font-semibold">1800-XXX-XXXX</div>
                  </div>
                </a>
                <a href="mailto:" className="flex items-center gap-3 p-3 bg-white/10 rounded-[var(--radius-lg)] hover:bg-white/20 transition-colors backdrop-blur-sm">
                  <Mail className="w-5 h-5" />
                  <div>
                    <div className="text-sm">Email Support</div>
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
              <h3 className="font-bold mb-2">Live Chat Support</h3>
              <p className="text-sm mb-4 text-white/90">Get instant help from our support team</p>
              <Button className="w-full bg-white text-[var(--secondary)] hover:bg-white/90 shadow-[var(--shadow-4)]">
                Start Chat
              </Button>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
