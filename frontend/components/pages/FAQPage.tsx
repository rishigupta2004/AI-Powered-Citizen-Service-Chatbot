import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Search,
  MessageCircle,
  Phone,
  Mail,
  HelpCircle,
  Book,
  Users,
  Shield,
} from "lucide-react";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../ui/card";
import { Textarea } from "../ui/textarea";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "../ui/accordion";
import { Badge } from "../ui/badge";
import { FloatingElements } from "../animations/FloatingElements";

interface FAQPageProps {
  onNavigate: (page: string) => void;
}

export function FAQPage({ onNavigate }: FAQPageProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] =
    useState("all");

  const categories = [
    { id: "all", name: "All Questions", count: 24, icon: Book },
    {
      id: "passport",
      name: "Passport Services",
      count: 8,
      icon: Shield,
    },
    {
      id: "aadhaar",
      name: "Aadhaar Services",
      count: 6,
      icon: Users,
    },
    {
      id: "epfo",
      name: "EPFO Services",
      count: 5,
      icon: HelpCircle,
    },
    {
      id: "general",
      name: "General Queries",
      count: 5,
      icon: MessageCircle,
    },
  ];

  const faqs = [
    {
      category: "passport",
      question: "How do I apply for a new passport?",
      answer:
        "To apply for a new passport, visit the Passport Services section, create an account if you haven't already, fill out the application form with your personal details, upload required documents, pay the application fee, and schedule an appointment at your nearest Passport Seva Kendra.",
    },
    {
      category: "passport",
      question:
        "What is the processing time for passport applications?",
      answer:
        "Regular passport applications are processed within 15-20 working days. Tatkal applications are processed within 3-5 working days. Processing time may vary based on police verification and document completeness.",
    },
    {
      category: "passport",
      question: "Can I track my passport application status?",
      answer:
        "Yes, you can track your passport application status using your application reference number on the tracking page. You will also receive SMS and email notifications at each stage of processing.",
    },
    {
      category: "passport",
      question:
        "What documents are required for passport application?",
      answer:
        "Required documents include: Proof of identity (Aadhaar, PAN, Voter ID), Proof of address (utility bills, rent agreement), Date of birth proof (birth certificate, school leaving certificate), and passport-size photographs.",
    },
    {
      category: "aadhaar",
      question: "How can I update my Aadhaar details?",
      answer:
        "You can update your Aadhaar details online through the Aadhaar Services section or by visiting your nearest Aadhaar enrollment center. Online updates are available for address, mobile number, and email.",
    },
    {
      category: "aadhaar",
      question: "Is there a fee for Aadhaar updates?",
      answer:
        "Yes, there is a nominal fee of ₹50 for updating demographic details and ₹100 for updating biometric information. The first update is free of charge.",
    },
    {
      category: "aadhaar",
      question: "How do I download my e-Aadhaar?",
      answer:
        "Visit the Aadhaar Services section, enter your 12-digit Aadhaar number or 16-digit enrollment ID, complete the OTP verification, and download your e-Aadhaar PDF. The password for the PDF is a combination of your name and date of birth.",
    },
    {
      category: "epfo",
      question: "How can I check my PF balance online?",
      answer:
        "Log in to the EPFO Services section using your UAN and password. Your current PF balance will be displayed on the dashboard. You can also download detailed passbooks and transaction history.",
    },
    {
      category: "epfo",
      question: "What is the process for PF withdrawal?",
      answer:
        "To withdraw PF, submit Form 19 (for full withdrawal) or Form 31 (for partial withdrawal) through the EPFO Services section. Claims are usually processed within 7-10 days after approval.",
    },
    {
      category: "epfo",
      question:
        "How do I transfer my PF from previous employer?",
      answer:
        "Submit Form 13 through the EPFO Services section with details of your previous employment. The transfer is usually completed within 7-15 days.",
    },
    {
      category: "general",
      question: "Is my data secure on this portal?",
      answer:
        "Yes, we use bank-grade 256-bit encryption, secure servers, and comply with ISO 27001 security standards. Your data is never shared with third parties without your explicit consent.",
    },
    {
      category: "general",
      question:
        "What are the system requirements to use this portal?",
      answer:
        "The portal works on all modern browsers (Chrome, Firefox, Safari, Edge). For best experience, use the latest version of your browser. Mobile apps are available for Android and iOS.",
    },
    {
      category: "general",
      question: "How can I contact customer support?",
      answer:
        "Our 24/7 support team is available via: Live chat (click the chat icon), Email (support@sevasindhu.gov.in), Phone (1800-XXX-XXXX), and through our FAQ section.",
    },
  ];

  const filteredFaqs = faqs.filter((faq) => {
    const matchesSearch =
      faq.question
        .toLowerCase()
        .includes(searchQuery.toLowerCase()) ||
      faq.answer
        .toLowerCase()
        .includes(searchQuery.toLowerCase());
    const matchesCategory =
      selectedCategory === "all" ||
      faq.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const contactMethods = [
    {
      icon: Phone,
      title: "Phone Support",
      description: "1800-XXX-XXXX",
      subtext: "Mon-Sat: 8 AM - 8 PM",
      color: "from-blue-500 to-blue-600",
    },
    {
      icon: Mail,
      title: "Email Support",
      description: "support@sevasindhu.gov.in",
      subtext: "24-hour response time",
      color: "from-purple-500 to-purple-600",
    },
    {
      icon: MessageCircle,
      title: "Live Chat",
      description: "Chat with our team",
      subtext: "Available 24/7",
      color: "from-green-500 to-green-600",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-[var(--background)] to-[var(--background-secondary)] pt-32 pb-20">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-[#000080] via-[#000066] to-[#000050] text-white py-20 mb-20 overflow-hidden">
        <FloatingElements count={8} className="opacity-20" />

        <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)] relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <Badge className="mb-6 bg-white/10 text-white border-white/20 backdrop-blur-sm px-6 py-2 text-base">
              Help Center
            </Badge>
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              Frequently Asked Questions
            </h1>
            <p className="text-xl text-white/90 max-w-3xl mx-auto leading-relaxed mb-8">
              Find answers to common questions about our
              services
            </p>

            {/* Search Bar */}
            <div className="max-w-2xl mx-auto">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/60" />
                <Input
                  type="text"
                  placeholder="Search for answers..."
                  value={searchQuery}
                  onChange={(e) =>
                    setSearchQuery(e.target.value)
                  }
                  className="pl-12 h-14 bg-white/10 border-white/20 text-white placeholder:text-white/60 backdrop-blur-sm"
                />
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)]">
        {/* Categories */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-12"
        >
          <div className="flex flex-wrap gap-3">
            {categories.map((category) => {
              const Icon = category.icon;
              return (
                <button
                  key={category.id}
                  onClick={() =>
                    setSelectedCategory(category.id)
                  }
                  className={`flex items-center gap-2 px-6 py-3 rounded-[var(--radius-lg)] border-2 transition-all ${
                    selectedCategory === category.id
                      ? "bg-[#000080] text-white border-[#000080] shadow-[var(--shadow-4)]"
                      : "bg-[var(--card)] text-[var(--foreground)] border-[var(--border)] hover:border-[#000080]"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="font-medium">
                    {category.name}
                  </span>
                  <Badge
                    variant={
                      selectedCategory === category.id
                        ? "secondary"
                        : "outline"
                    }
                    className="text-xs"
                  >
                    {category.count}
                  </Badge>
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* FAQ Accordion */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-20">
          {/* FAQ List */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card className="border-2 border-[var(--card-border)] shadow-[var(--shadow-8)] bg-[var(--card)]">
                <CardHeader>
                  <CardTitle className="text-2xl text-[var(--foreground)]">
                    {selectedCategory === "all"
                      ? "All Questions"
                      : categories.find(
                          (c) => c.id === selectedCategory,
                        )?.name}
                  </CardTitle>
                  <CardDescription className="text-[var(--muted-foreground)]">
                    Showing {filteredFaqs.length} question
                    {filteredFaqs.length !== 1 ? "s" : ""}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {filteredFaqs.length > 0 ? (
                    <Accordion
                      type="single"
                      collapsible
                      className="w-full"
                    >
                      {filteredFaqs.map((faq, index) => (
                        <AccordionItem
                          key={index}
                          value={`item-${index}`}
                          className="border-[var(--border)]"
                        >
                          <AccordionTrigger className="text-left hover:text-[#000080] text-[var(--foreground)]">
                            <span className="font-medium">
                              {faq.question}
                            </span>
                          </AccordionTrigger>
                          <AccordionContent className="text-[var(--muted-foreground)] leading-relaxed">
                            {faq.answer}
                          </AccordionContent>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  ) : (
                    <div className="text-center py-12">
                      <Search className="w-12 h-12 text-[var(--muted-foreground)] mx-auto mb-4" />
                      <p className="text-[var(--muted-foreground)]">
                        No questions found matching "
                        {searchQuery}"
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Contact Methods Sidebar */}
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="space-y-4 sticky top-32"
            >
              <Card className="border-2 border-[var(--card-border)] shadow-[var(--shadow-8)] bg-[var(--card)]">
                <CardHeader>
                  <CardTitle className="text-xl text-[var(--foreground)]">
                    Still Need Help?
                  </CardTitle>
                  <CardDescription className="text-[var(--muted-foreground)]">
                    Our support team is here for you
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {contactMethods.map((method, index) => {
                    const Icon = method.icon;
                    return (
                      <div
                        key={index}
                        className="p-4 border-2 border-[var(--border)] rounded-[var(--radius-lg)] hover:border-[#000080] hover:shadow-[var(--shadow-4)] transition-all group"
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className={`w-12 h-12 bg-gradient-to-br ${method.color} rounded-[var(--radius-lg)] flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform`}
                          >
                            <Icon className="w-6 h-6 text-white" />
                          </div>
                          <div className="flex-1">
                            <div className="font-semibold text-[var(--foreground)] mb-1">
                              {method.title}
                            </div>
                            <div className="text-sm text-[var(--muted-foreground)] mb-1">
                              {method.description}
                            </div>
                            <div className="text-xs text-[var(--muted-foreground)]">
                              {method.subtext}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>

              {/* Quick Links */}
              <Card className="border-2 border-[var(--card-border)] bg-[var(--card)]">
                <CardHeader>
                  <CardTitle className="text-lg text-[var(--foreground)]">
                    Quick Links
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-[var(--foreground)] hover:text-[#000080] hover:bg-[#000080]/10"
                    onClick={() => onNavigate("services")}
                  >
                    Browse Services
                  </Button>
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-[var(--foreground)] hover:text-[#000080] hover:bg-[#000080]/10"
                    onClick={() => onNavigate("dashboard")}
                  >
                    My Dashboard
                  </Button>
                  <Button
                    variant="ghost"
                    className="w-full justify-start text-[var(--foreground)] hover:text-[#000080] hover:bg-[#000080]/10"
                    onClick={() => onNavigate("about")}
                  >
                    About Us
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>

        {/* Contact Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <Card className="border-2 border-[var(--card-border)] shadow-[var(--shadow-8)] bg-[var(--card)]">
            <CardHeader>
              <CardTitle className="text-2xl text-[var(--foreground)]">
                Can't Find Your Answer?
              </CardTitle>
              <CardDescription className="text-[var(--muted-foreground)]">
                Send us a message and we'll get back to you
                within 24 hours
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-[var(--foreground)] mb-2 block">
                      Your Name
                    </label>
                    <Input
                      type="text"
                      placeholder="Enter your name"
                      className="bg-[var(--input-background)] text-[var(--foreground)] border-[var(--border)]"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-[var(--foreground)] mb-2 block">
                      Email Address
                    </label>
                    <Input
                      type="email"
                      placeholder="your.email@example.com"
                      className="bg-[var(--input-background)] text-[var(--foreground)] border-[var(--border)]"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-[var(--foreground)] mb-2 block">
                    Subject
                  </label>
                  <Input
                    type="text"
                    placeholder="What is your question about?"
                    className="bg-[var(--input-background)] text-[var(--foreground)] border-[var(--border)]"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-[var(--foreground)] mb-2 block">
                    Message
                  </label>
                  <Textarea
                    placeholder="Describe your question in detail..."
                    rows={6}
                    className="bg-[var(--input-background)] text-[var(--foreground)] border-[var(--border)]"
                  />
                </div>
                <Button
                  size="lg"
                  className="bg-[#000080] text-white hover:bg-[#000066]"
                >
                  Send Message
                </Button>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}