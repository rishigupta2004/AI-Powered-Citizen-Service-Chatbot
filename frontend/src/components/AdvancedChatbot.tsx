import React, { useState, useRef, useEffect } from "react";
import {
  MessageCircle,
  X,
  Send,
  Loader2,
  CheckCircle2,
  Paperclip,
  Mic,
  Sparkles,
  FileText,
  Calendar,
  CreditCard,
  ArrowRight,
  Bot,
  User as UserIcon,
  Home,
  AlertCircle,
  Phone,
  Mail,
  ChevronRight,
  ExternalLink,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
} from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { ScrollArea } from "./ui/scroll-area";
import { motion, AnimatePresence } from "motion/react";
import { cn } from "./ui/utils";
import { toast } from "sonner@2.0.3";
import { Badge } from "./ui/badge";
import { Card, CardContent } from "./ui/card";
import { getAllServices } from "../data/servicesData";
import { useAuth } from "./AuthContext";

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
  type?: "text" | "service-card" | "quick-actions" | "form";
  data?: any;
  isTyping?: boolean;
}

interface QuickAction {
  id: string;
  icon: any;
  label: string;
  description: string;
  action: string;
}

interface AdvancedChatbotProps {
  onNavigate?: (page: string, serviceId?: string) => void;
  currentPage?: string;
  currentService?: string;
}

export function AdvancedChatbot({ onNavigate, currentPage = 'home', currentService }: AdvancedChatbotProps) {
  const { user, isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [currentStep, setCurrentStep] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [inputElement, setInputElement] = useState<HTMLInputElement | null>(null);

  const allServices = getAllServices();

  // Welcome message with quick actions - context aware
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setTimeout(() => {
        let welcomeMessage = isAuthenticated && user
          ? `नमस्ते ${user.name}! Welcome back to Seva Sindhu AI Assistant 🇮🇳\n\n`
          : "नमस्ते! Welcome to Seva Sindhu AI Assistant 🇮🇳\n\n";
        
        // Add context-specific greeting
        if (currentPage === 'dashboard' && isAuthenticated) {
          welcomeMessage += "I can see you're on your dashboard. I can help you track applications, check status, or start a new service.";
        } else if (currentPage === 'services') {
          welcomeMessage += "Looking for a specific service? I can help you find and apply for the right government service.";
        } else if (currentPage === 'service-detail' && currentService) {
          welcomeMessage += `I can help you with ${currentService}. Would you like to know about requirements, process, or start the application?`;
        } else if (currentPage === 'tracker' && isAuthenticated) {
          welcomeMessage += "I can help you track your applications. Just provide your Application Reference Number (ARN).";
        } else {
          welcomeMessage += "I'm here to help you with government services. How can I assist you today?";
        }
        
        addBotMessage(welcomeMessage, "text");
        
        setTimeout(() => {
          addBotMessage("", "quick-actions", {
            actions: quickActions,
          });
        }, 800);
      }, 300);
    }
  }, [isOpen, currentPage, currentService, isAuthenticated, user]);

  // Context-aware quick actions
  const getQuickActions = (): QuickAction[] => {
    const baseActions = [
      {
        id: "apply-service",
        icon: FileText,
        label: "Apply for Service",
        description: "Start a new application",
        action: "show-services",
      },
      {
        id: "track-application",
        icon: Calendar,
        label: "Track Application",
        description: "Check application status",
        action: "track",
      },
      {
        id: "update-details",
        icon: CreditCard,
        label: "Update Details",
        description: "Update Aadhaar/PAN/other",
        action: "update",
      },
      {
        id: "help-support",
        icon: Phone,
        label: "Help & Support",
        description: "24/7 assistance",
        action: "support",
      },
    ];

    // Add context-specific actions
    if (currentPage === 'dashboard') {
      return [
        {
          id: "view-applications",
          icon: FileText,
          label: "My Applications",
          description: "View all applications",
          action: "dashboard-apps",
        },
        ...baseActions.slice(1),
      ];
    } else if (currentPage === 'services') {
      return [
        {
          id: "popular-services",
          icon: Sparkles,
          label: "Popular Services",
          description: "Most used services",
          action: "show-popular",
        },
        ...baseActions,
      ];
    }

    return baseActions;
  };

  const quickActions = getQuickActions();

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputElement) {
      setTimeout(() => inputElement.focus(), 300);
    }
  }, [isOpen, inputElement]);

  const addBotMessage = (text: string, type: string = "text", data?: any) => {
    const botMessage: Message = {
      id: Date.now().toString() + Math.random(),
      text,
      sender: "bot",
      timestamp: new Date(),
      type: type as any,
      data,
    };
    setMessages((prev) => [...prev, botMessage]);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: "user",
      timestamp: new Date(),
      type: "text",
    };

    setMessages((prev) => [...prev, userMessage]);
    const query = inputValue.toLowerCase();
    setInputValue("");
    setIsTyping(true);

    // Simulate AI processing
    setTimeout(() => {
      setIsTyping(false);
      handleIntelligentResponse(query);
    }, 1000 + Math.random() * 1000);
  };

  const handleIntelligentResponse = (query: string) => {
    // Service-related queries
    if (
      query.includes("passport") ||
      query.includes("apply") ||
      query.includes("service")
    ) {
      addBotMessage(
        "I can help you with passport services! Let me show you the available options:",
        "text"
      );
      setTimeout(() => {
        const passportServices = allServices.filter((s) =>
          s.name.toLowerCase().includes("passport")
        );
        addBotMessage("", "service-card", {
          services: passportServices.slice(0, 3),
        });
      }, 500);
    }
    // Aadhaar queries
    else if (query.includes("aadhaar") || query.includes("aadhar")) {
      addBotMessage(
        "I can assist you with Aadhaar services. What would you like to do?",
        "text"
      );
      setTimeout(() => {
        const aadhaarServices = allServices.filter((s) =>
          s.name.toLowerCase().includes("aadhaar")
        );
        addBotMessage("", "service-card", {
          services: aadhaarServices,
        });
      }, 500);
    }
    // Tracking queries
    else if (
      query.includes("track") ||
      query.includes("status") ||
      query.includes("application")
    ) {
      addBotMessage(
        "To track your application, I'll need some details. Please provide your Application Reference Number (ARN):",
        "text"
      );
      setCurrentStep("awaiting-arn");
    }
    // Help queries
    else if (
      query.includes("help") ||
      query.includes("support") ||
      query.includes("contact")
    ) {
      addBotMessage(
        "I'm here to help! You can reach our support team through:",
        "text"
      );
      setTimeout(() => {
        addBotMessage("", "quick-actions", {
          actions: [
            {
              id: "phone",
              icon: Phone,
              label: "Call Us",
              description: "1800-XXX-XXXX (Toll-free)",
              action: "call",
            },
            {
              id: "email",
              icon: Mail,
              label: "Email Us",
              description: "support@sevasindhu.gov.in",
              action: "email",
            },
            {
              id: "faq",
              icon: FileText,
              label: "Browse FAQ",
              description: "Find instant answers",
              action: "faq",
            },
          ],
        });
      }, 500);
    }
    // Show all services
    else if (query.includes("show") || query.includes("list") || query.includes("all")) {
      addBotMessage(
        "Here are our most popular government services:",
        "text"
      );
      setTimeout(() => {
        addBotMessage("", "service-card", {
          services: allServices.slice(0, 6),
        });
      }, 500);
    }
    // Generic response with smart suggestions
    else {
      const response = generateSmartResponse(query);
      addBotMessage(response, "text");
      
      // Show related services if applicable
      const relatedServices = findRelatedServices(query);
      if (relatedServices.length > 0) {
        setTimeout(() => {
          addBotMessage("I found these related services:", "text");
          setTimeout(() => {
            addBotMessage("", "service-card", {
              services: relatedServices.slice(0, 3),
            });
          }, 500);
        }, 1000);
      }
    }
  };

  const generateSmartResponse = (query: string): string => {
    const responses = [
      "I understand you're asking about that. Let me help you find the right service or information.",
      "That's a great question! I'm here to guide you through our government services.",
      "I can definitely assist you with that. Let me provide you with the relevant information.",
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const findRelatedServices = (query: string) => {
    return allServices.filter((service) =>
      service.name.toLowerCase().includes(query) ||
      service.description.toLowerCase().includes(query) ||
      service.category.toLowerCase().includes(query)
    );
  };

  const handleQuickAction = (action: string) => {
    switch (action) {
      case "show-services":
        addBotMessage("Here are all our available services:", "text");
        setTimeout(() => {
          addBotMessage("", "service-card", {
            services: allServices.slice(0, 6),
          });
        }, 500);
        break;
      case "show-popular":
        addBotMessage("Here are our most popular services:", "text");
        setTimeout(() => {
          const popularServices = allServices.filter(s => 
            s.badge === 'Popular' || s.badge === 'Featured'
          );
          addBotMessage("", "service-card", {
            services: popularServices.length > 0 ? popularServices.slice(0, 6) : allServices.slice(0, 6),
          });
        }, 500);
        break;
      case "dashboard-apps":
        if (onNavigate) {
          onNavigate("dashboard");
          toast.success("Opening your dashboard");
        }
        addBotMessage(
          "I've opened your dashboard. You can view all your applications, track their status, and see recent activity there.",
          "text"
        );
        break;
      case "track":
        addBotMessage(
          "To track your application, please provide your Application Reference Number (ARN):\n\nExample: PS12345678 or DL98765432",
          "text"
        );
        setCurrentStep("awaiting-arn");
        break;
      case "update":
        addBotMessage(
          "Which document would you like to update?",
          "text"
        );
        setTimeout(() => {
          const updateServices = allServices.filter(s => 
            s.name.toLowerCase().includes('update') || 
            s.name.toLowerCase().includes('correction')
          );
          if (updateServices.length > 0) {
            addBotMessage("", "service-card", {
              services: updateServices,
            });
          }
        }, 500);
        break;
      case "support":
        handleIntelligentResponse("help");
        break;
      case "faq":
        if (onNavigate) onNavigate("faq");
        toast.success("Opening FAQ page");
        break;
      case "call":
        toast.info("Toll-free: 1800-XXX-XXXX (Available 24/7)");
        break;
      case "email":
        toast.info("Email: support@sevasindhu.gov.in");
        break;
      default:
        break;
    }
  };

  const handleServiceClick = (serviceId: string) => {
    if (onNavigate) {
      onNavigate("service-detail", serviceId);
      setIsOpen(false);
      toast.success("Opening service details");
    }
  };

  const handleFeedback = (messageId: string, isPositive: boolean) => {
    toast.success(
      isPositive
        ? "Thank you for your feedback!"
        : "We'll work on improving our responses"
    );
  };

  return (
    <>
      {/* Floating Chat Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{
              type: "spring",
              stiffness: 300,
              damping: 25,
            }}
            className="fixed bottom-6 right-6 z-[var(--z-fixed)]"
          >
            <Button
              onClick={() => setIsOpen(true)}
              size="lg"
              className="relative w-16 h-16 rounded-full bg-gradient-to-br from-[#000080] to-[#000066] hover:from-[#000066] hover:to-[#000050] shadow-2xl hover:shadow-[0_20px_60px_-15px_rgba(0,0,128,0.6)] transition-all duration-300 group overflow-hidden"
              aria-label="Open AI assistant"
            >
              {/* Animated gradient background */}
              <div className="absolute inset-0 bg-gradient-to-r from-[#FF9933] via-transparent to-[#138808] opacity-0 group-hover:opacity-20 transition-opacity" />
              
              {/* Icon with animation */}
              <motion.div
                animate={{
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  repeatDelay: 2,
                }}
                className="relative z-10"
              >
                <Sparkles className="w-7 h-7 text-white group-hover:scale-110 transition-transform" />
              </motion.div>

              {/* Pulse indicator */}
              <span className="absolute -top-1 -right-1 flex h-5 w-5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#FF9933] opacity-75" />
                <span className="relative inline-flex rounded-full h-5 w-5 bg-[#FF9933] items-center justify-center">
                  <span className="w-2 h-2 bg-white rounded-full" />
                </span>
              </span>
            </Button>

            {/* Enhanced Tooltip */}
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
              className="absolute bottom-full right-0 mb-4 pointer-events-none"
            >
              <div className="bg-gradient-to-r from-[#000080] to-[#000066] text-white rounded-2xl shadow-2xl px-6 py-4 min-w-[280px]">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-full flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <div className="font-bold text-lg">AI Assistant</div>
                    <div className="text-xs text-white/80">Powered by Seva Sindhu</div>
                  </div>
                </div>
                <div className="text-sm text-white/90 leading-relaxed">
                  Ask me anything about government services, applications, or tracking!
                </div>
                <div className="mt-3 flex items-center gap-2 text-xs text-white/70">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  Available 24/7 • Instant responses
                </div>
              </div>
              <div className="absolute top-full right-8 w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-[#000066]" />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Advanced Chat Interface */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{
              type: "spring",
              stiffness: 300,
              damping: 30,
            }}
            className="fixed bottom-6 right-6 w-full max-w-[440px] z-[var(--z-modal)] shadow-2xl"
            role="dialog"
            aria-labelledby="chat-title"
            aria-modal="true"
          >
            <div className="bg-[var(--card)] rounded-3xl overflow-hidden border-2 border-[var(--border)] shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25)]">
              {/* Header */}
              <div className="relative bg-gradient-to-r from-[#000080] via-[#000066] to-[#000050] px-6 py-5 overflow-hidden">
                {/* Animated background pattern */}
                <div className="absolute inset-0 opacity-10">
                  <div
                    className="absolute inset-0"
                    style={{
                      backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
                    }}
                  />
                </div>

                <div className="relative flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="relative">
                      <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center border border-white/20">
                        <Bot className="w-6 h-6 text-white" />
                      </div>
                      <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-[#000066] animate-pulse" />
                    </div>
                    <div>
                      <div id="chat-title" className="text-white font-bold text-lg">
                        Seva Sindhu AI
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                        <span className="text-white/90">Always Online • Instant Help</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setMessages([]);
                        setCurrentStep(null);
                        toast.success("Chat cleared");
                      }}
                      className="text-white hover:bg-white/10 rounded-full"
                      aria-label="Clear chat"
                    >
                      <RotateCcw className="w-5 h-5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setIsOpen(false)}
                      className="text-white hover:bg-white/10 rounded-full"
                      aria-label="Close chat"
                    >
                      <X className="w-5 h-5" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Messages Area */}
              <ScrollArea className="h-[500px] p-6 bg-gradient-to-b from-[var(--background)] to-[var(--background-secondary)]">
                <div className="space-y-6">
                  {messages.map((message, index) => (
                    <div key={message.id}>
                      {message.type === "text" && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className={cn(
                            "flex gap-3",
                            message.sender === "user" ? "justify-end" : "justify-start"
                          )}
                        >
                          {message.sender === "bot" && (
                            <div className="w-8 h-8 bg-gradient-to-br from-[#000080] to-[#000066] rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                              <Bot className="w-4 h-4 text-white" />
                            </div>
                          )}
                          <div className="flex flex-col gap-2 max-w-[80%]">
                            <div
                              className={cn(
                                "rounded-2xl px-5 py-3 shadow-md",
                                message.sender === "user"
                                  ? "bg-gradient-to-br from-[#000080] to-[#000066] text-white rounded-br-sm"
                                  : "bg-[var(--card)] text-[var(--foreground)] border-2 border-[var(--border)] rounded-bl-sm"
                              )}
                            >
                              <p className="text-sm leading-relaxed whitespace-pre-line">
                                {message.text}
                              </p>
                              <div
                                className={cn(
                                  "text-xs mt-2 flex items-center gap-2",
                                  message.sender === "user"
                                    ? "text-white/70 justify-end"
                                    : "text-[var(--muted-foreground)]"
                                )}
                              >
                                <time>
                                  {message.timestamp.toLocaleTimeString([], {
                                    hour: "2-digit",
                                    minute: "2-digit",
                                  })}
                                </time>
                                {message.sender === "user" && (
                                  <CheckCircle2 className="w-3 h-3" />
                                )}
                              </div>
                            </div>
                            {message.sender === "bot" && (
                              <div className="flex items-center gap-2 px-2">
                                <button
                                  onClick={() => handleFeedback(message.id, true)}
                                  className="text-[var(--muted-foreground)] hover:text-green-600 transition-colors"
                                  aria-label="Helpful"
                                >
                                  <ThumbsUp className="w-3 h-3" />
                                </button>
                                <button
                                  onClick={() => handleFeedback(message.id, false)}
                                  className="text-[var(--muted-foreground)] hover:text-red-600 transition-colors"
                                  aria-label="Not helpful"
                                >
                                  <ThumbsDown className="w-3 h-3" />
                                </button>
                              </div>
                            )}
                          </div>
                          {message.sender === "user" && (
                            <div className="w-8 h-8 bg-gradient-to-br from-[#FF9933] to-[#FF7700] rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                              <UserIcon className="w-4 h-4 text-white" />
                            </div>
                          )}
                        </motion.div>
                      )}

                      {message.type === "service-card" && message.data?.services && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex gap-3"
                        >
                          <div className="w-8 h-8 bg-gradient-to-br from-[#000080] to-[#000066] rounded-full flex items-center justify-center flex-shrink-0">
                            <Sparkles className="w-4 h-4 text-white" />
                          </div>
                          <div className="flex-1 space-y-3">
                            {message.data.services.map((service: any, idx: number) => (
                              <motion.div
                                key={service.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.1 }}
                              >
                                <Card
                                  className="border-2 border-[var(--border)] hover:border-[#000080] hover:shadow-lg transition-all cursor-pointer group"
                                  onClick={() => handleServiceClick(service.id)}
                                >
                                  <CardContent className="p-4">
                                    <div className="flex items-start gap-3">
                                      <div
                                        className={`w-12 h-12 bg-gradient-to-br ${service.gradient} rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform`}
                                      >
                                        <service.icon className="w-6 h-6 text-white" />
                                      </div>
                                      <div className="flex-1 min-w-0">
                                        <div className="flex items-start justify-between gap-2 mb-1">
                                          <h4 className="font-semibold text-[var(--foreground)] group-hover:text-[#000080] transition-colors">
                                            {service.name}
                                          </h4>
                                          {service.badge && (
                                            <Badge variant="secondary" className="text-xs">
                                              {service.badge}
                                            </Badge>
                                          )}
                                        </div>
                                        <p className="text-sm text-[var(--muted-foreground)] mb-2">
                                          {service.description}
                                        </p>
                                        <div className="flex items-center gap-3 text-xs text-[var(--muted-foreground)]">
                                          <span>⏱️ {service.processingTime}</span>
                                          <span>•</span>
                                          <span>💰 {service.fee}</span>
                                        </div>
                                      </div>
                                      <ChevronRight className="w-5 h-5 text-[var(--muted-foreground)] group-hover:text-[#000080] group-hover:translate-x-1 transition-all" />
                                    </div>
                                  </CardContent>
                                </Card>
                              </motion.div>
                            ))}
                            <Button
                              variant="outline"
                              size="sm"
                              className="w-full border-[var(--border)] text-[var(--foreground)]"
                              onClick={() => {
                                if (onNavigate) onNavigate("services");
                                toast.success("Opening all services");
                              }}
                            >
                              View All Services
                              <ExternalLink className="w-4 h-4 ml-2" />
                            </Button>
                          </div>
                        </motion.div>
                      )}

                      {message.type === "quick-actions" && message.data?.actions && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex gap-3"
                        >
                          <div className="w-8 h-8 bg-gradient-to-br from-[#138808] to-[#0F6606] rounded-full flex items-center justify-center flex-shrink-0">
                            <Sparkles className="w-4 h-4 text-white" />
                          </div>
                          <div className="flex-1 grid grid-cols-2 gap-3">
                            {message.data.actions.map((action: QuickAction, idx: number) => (
                              <motion.div
                                key={action.id}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: idx * 0.1 }}
                              >
                                <Card
                                  className="border-2 border-[var(--border)] hover:border-[#000080] hover:shadow-md transition-all cursor-pointer group"
                                  onClick={() => handleQuickAction(action.action)}
                                >
                                  <CardContent className="p-4 text-center">
                                    <div className="w-12 h-12 bg-gradient-to-br from-[#000080] to-[#000066] rounded-xl flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                                      <action.icon className="w-6 h-6 text-white" />
                                    </div>
                                    <div className="font-semibold text-sm text-[var(--foreground)] mb-1">
                                      {action.label}
                                    </div>
                                    <div className="text-xs text-[var(--muted-foreground)]">
                                      {action.description}
                                    </div>
                                  </CardContent>
                                </Card>
                              </motion.div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </div>
                  ))}

                  {/* Scroll anchor */}
                  <div ref={messagesEndRef} />

                  {/* Typing Indicator */}
                  {isTyping && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex gap-3"
                    >
                      <div className="w-8 h-8 bg-gradient-to-br from-[#000080] to-[#000066] rounded-full flex items-center justify-center flex-shrink-0">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <div className="bg-[var(--card)] border-2 border-[var(--border)] rounded-2xl rounded-bl-sm px-5 py-4 shadow-md">
                        <div className="flex gap-1">
                          {[0, 1, 2].map((i) => (
                            <motion.div
                              key={i}
                              animate={{ y: [-2, 2, -2] }}
                              transition={{
                                duration: 0.6,
                                repeat: Infinity,
                                delay: i * 0.15,
                              }}
                              className="w-2 h-2 bg-[#000080] rounded-full"
                            />
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </div>
              </ScrollArea>

              {/* Input Area */}
              <div className="p-4 bg-[var(--card)] border-t-2 border-[var(--border)]">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="flex gap-2"
                >
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="flex-shrink-0 text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                    aria-label="Attach file"
                    onClick={() => toast.info("File upload coming soon")}
                  >
                    <Paperclip className="w-5 h-5" />
                  </Button>
                  <Input
                    type="text"
                    placeholder="Ask anything about government services..."
                    value={inputValue}
                    onChange={(e) => {
                      setInputValue(e.target.value);
                      if (!inputElement && e.target instanceof HTMLInputElement) {
                        setInputElement(e.target);
                      }
                    }}
                    className="flex-1 h-12 bg-[var(--input-background)] border-[var(--border)] text-[var(--foreground)]"
                    aria-label="Chat message input"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="flex-shrink-0 text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                    aria-label="Voice input"
                    onClick={() => toast.info("Voice input coming soon")}
                  >
                    <Mic className="w-5 h-5" />
                  </Button>
                  <Button
                    type="submit"
                    size="icon"
                    className="bg-gradient-to-br from-[#000080] to-[#000066] hover:from-[#000066] hover:to-[#000050] flex-shrink-0 h-12 w-12"
                    disabled={!inputValue.trim()}
                    aria-label="Send message"
                  >
                    <Send className="w-5 h-5" />
                  </Button>
                </form>
                <div className="text-xs text-[var(--muted-foreground)] mt-3 text-center flex items-center justify-center gap-2">
                  <Sparkles className="w-3 h-3" />
                  <span>Powered by AI • Secure & Confidential • Available 24/7</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
