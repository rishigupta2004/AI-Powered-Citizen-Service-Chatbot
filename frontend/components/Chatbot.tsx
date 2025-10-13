import React, { useState, useRef, useEffect } from "react";
import {
  MessageCircle,
  X,
  Send,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Paperclip,
  WifiOff,
} from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { ScrollArea } from "./ui/scroll-area";
import { motion, AnimatePresence } from "motion/react";
import { cn } from "./ui/utils";
import { toast } from "sonner@2.0.3";

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
  status?: "sending" | "sent" | "error";
}

export function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "Hello! Welcome to Government Citizen Services. How can I assist you today?",
      sender: "bot",
      timestamp: new Date(),
      status: "sent",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const suggestedQueries = [
    "How to apply for passport?",
    "Aadhaar update process",
    "EPFO claim status",
    "Scholarship eligibility",
    "Track application",
  ];

  // Monitor online status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      toast.success("Connection restored");
    };

    const handleOffline = () => {
      setIsOnline(false);
      toast.error(
        "Connection lost. Please check your internet.",
      );
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop =
        scrollAreaRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  // Handle Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        setIsOpen(false);
      }
    };
    window.addEventListener("keydown", handleEscape);
    return () =>
      window.removeEventListener("keydown", handleEscape);
  }, [isOpen]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !isOnline) {
      if (!isOnline) {
        toast.error("Cannot send message while offline");
      }
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: "user",
      timestamp: new Date(),
      status: "sending",
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    // Announce to screen readers
    const announcement = `You said: ${inputValue}`;
    const liveRegion = document.getElementById(
      "chat-live-region",
    );
    if (liveRegion) {
      liveRegion.textContent = announcement;
    }

    // Simulate bot response
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: `I understand you're asking about "${inputValue}". Let me help you with that. For detailed information, please visit our services section or contact our support team at 1800-XXX-XXXX.`,
        sender: "bot",
        timestamp: new Date(),
        status: "sent",
      };
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === userMessage.id
            ? { ...msg, status: "sent" }
            : msg,
        ),
      );
      setIsTyping(false);
      setMessages((prev) => [...prev, botMessage]);

      // Announce bot response
      if (liveRegion) {
        liveRegion.textContent = `Bot responded: ${botMessage.text}`;
      }
    }, 1500);
  };

  const handleSuggestedQuery = (query: string) => {
    setInputValue(query);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  return (
    <>
      {/* Live Region for Screen Reader Announcements */}
      <div
        id="chat-live-region"
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      />

      {/* Chat Widget Button */}
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
              className="w-16 h-16 rounded-full bg-gradient-to-br from-[var(--primary)] to-[var(--primary-hover)] hover:from-[var(--primary-hover)] hover:to-[var(--primary-active)] shadow-[var(--shadow-12)] hover:shadow-[var(--shadow-24)] transition-all duration-[var(--transition-base)] group relative overflow-hidden"
              aria-label="Open chat support"
            >
              <motion.div
                animate={{
                  scale: [1, 1.1, 1],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  repeatDelay: 3,
                }}
              >
                <MessageCircle className="w-7 h-7 text-[var(--primary-foreground)] group-hover:scale-110 transition-transform" />
              </motion.div>
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-[var(--accent)] rounded-full animate-pulse flex items-center justify-center">
                <span className="w-2 h-2 bg-white rounded-full" />
              </span>
            </Button>

            {/* Tooltip */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="absolute bottom-full right-0 mb-3 bg-[var(--card)] rounded-[var(--radius-lg)] shadow-[var(--shadow-8)] px-4 py-2 text-sm whitespace-nowrap pointer-events-none"
            >
              <div className="text-[var(--foreground)] font-medium">
                Need help?
              </div>
              <div className="text-[var(--muted-foreground)] text-xs">
                Chat with us 24/7
              </div>
              <div className="absolute top-full right-6 w-0 h-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-[var(--card)]" />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Modal */}
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
            className="fixed bottom-6 right-6 w-full max-w-md z-[var(--z-modal)]"
            role="dialog"
            aria-labelledby="chat-title"
            aria-modal="true"
          >
            <div className="glass-effect rounded-[var(--radius-2xl)] shadow-[var(--shadow-24)] overflow-hidden border-2 border-[var(--card-border)]">
              {/* Header */}
              <div className="bg-gradient-to-r from-[var(--primary)] to-[var(--primary-hover)] px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 glass-effect rounded-full flex items-center justify-center">
                    <MessageCircle className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <div
                      id="chat-title"
                      className="text-white font-semibold"
                    >
                      GovBot Assistant
                    </div>
                    <div className="flex items-center gap-2">
                      {isOnline ? (
                        <>
                          <div className="w-2 h-2 bg-[var(--accent)] rounded-full animate-pulse" />
                          <span className="text-xs text-white/80">
                            Online
                          </span>
                        </>
                      ) : (
                        <>
                          <WifiOff className="w-3 h-3 text-white/80" />
                          <span className="text-xs text-white/80">
                            Offline
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
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

              {/* Messages Area */}
              <ScrollArea
                className="h-96 p-4 bg-[var(--background-secondary)]"
                ref={scrollAreaRef}
                role="log"
                aria-label="Chat messages"
              >
                <div className="space-y-4">
                  {messages.map((message, index) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={cn(
                        "flex",
                        message.sender === "user"
                          ? "justify-end"
                          : "justify-start",
                      )}
                    >
                      <div
                        className={cn(
                          "max-w-[80%] rounded-[var(--radius-2xl)] px-4 py-3 shadow-[var(--shadow-2)]",
                          message.sender === "user"
                            ? "bg-[var(--primary)] text-[var(--primary-foreground)] rounded-br-sm"
                            : "bg-[var(--card)] text-[var(--card-foreground)] rounded-bl-sm border border-[var(--card-border)]",
                        )}
                        role="article"
                        aria-label={`${message.sender === "user" ? "Your" : "Bot"} message`}
                      >
                        <p className="text-sm leading-relaxed">
                          {message.text}
                        </p>
                        <div
                          className={cn(
                            "text-xs mt-1 flex items-center gap-1 justify-end",
                            message.sender === "user"
                              ? "text-[var(--primary-foreground)]/70"
                              : "text-[var(--muted-foreground)]",
                          )}
                        >
                          <time
                            dateTime={message.timestamp.toISOString()}
                          >
                            {message.timestamp.toLocaleTimeString(
                              [],
                              {
                                hour: "2-digit",
                                minute: "2-digit",
                              },
                            )}
                          </time>
                          {message.sender === "user" &&
                            message.status === "sent" && (
                              <CheckCircle2
                                className="w-3 h-3"
                                aria-label="Message sent"
                              />
                            )}
                          {message.sender === "user" &&
                            message.status === "sending" && (
                              <Loader2
                                className="w-3 h-3 animate-spin"
                                aria-label="Sending message"
                              />
                            )}
                          {message.sender === "user" &&
                            message.status === "error" && (
                              <AlertCircle
                                className="w-3 h-3"
                                aria-label="Message failed"
                              />
                            )}
                        </div>
                      </div>
                    </motion.div>
                  ))}

                  {/* Typing Indicator */}
                  {isTyping && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex justify-start"
                      role="status"
                      aria-label="Bot is typing"
                    >
                      <div className="bg-[var(--card)] text-[var(--card-foreground)] rounded-[var(--radius-2xl)] rounded-bl-sm px-4 py-3 shadow-[var(--shadow-2)] border border-[var(--card-border)]">
                        <div
                          className="flex gap-1"
                          aria-hidden="true"
                        >
                          <motion.div
                            animate={{ y: [-2, 2, -2] }}
                            transition={{
                              duration: 0.6,
                              repeat: Infinity,
                              delay: 0,
                            }}
                            className="w-2 h-2 bg-[var(--muted-foreground)] rounded-full"
                          />
                          <motion.div
                            animate={{ y: [-2, 2, -2] }}
                            transition={{
                              duration: 0.6,
                              repeat: Infinity,
                              delay: 0.15,
                            }}
                            className="w-2 h-2 bg-[var(--muted-foreground)] rounded-full"
                          />
                          <motion.div
                            animate={{ y: [-2, 2, -2] }}
                            transition={{
                              duration: 0.6,
                              repeat: Infinity,
                              delay: 0.3,
                            }}
                            className="w-2 h-2 bg-[var(--muted-foreground)] rounded-full"
                          />
                        </div>
                        <span className="sr-only">
                          Bot is typing
                        </span>
                      </div>
                    </motion.div>
                  )}
                </div>
              </ScrollArea>

              {/* Offline Banner */}
              {!isOnline && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="px-4 py-2 bg-[var(--error-bg)] border-t border-[var(--error-border)] text-[var(--error)] text-sm flex items-center justify-center gap-2"
                  role="alert"
                >
                  <WifiOff className="w-4 h-4" />
                  You're offline. Messages will be sent when
                  connection is restored.
                </motion.div>
              )}

              {/* Suggested Queries */}
              {messages.length === 1 && (
                <div className="px-4 py-3 bg-[var(--card)] border-t border-[var(--border)]">
                  <div className="text-xs text-[var(--muted-foreground)] mb-2 font-medium">
                    Quick questions:
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {suggestedQueries
                      .slice(0, 3)
                      .map((query, index) => (
                        <button
                          key={index}
                          onClick={() =>
                            handleSuggestedQuery(query)
                          }
                          className="text-xs px-3 py-1.5 bg-[var(--muted)] hover:bg-[var(--muted)]/70 text-[var(--foreground)] rounded-full transition-colors duration-[var(--transition-fast)] focus-visible:ring-[var(--focus-ring-width)] focus-visible:ring-[var(--focus-ring-color)]"
                        >
                          {query}
                        </button>
                      ))}
                  </div>
                </div>
              )}

              {/* Input Area */}
              <div className="p-4 bg-[var(--card)] border-t border-[var(--border)]">
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
                    className="flex-shrink-0"
                    aria-label="Attach file"
                    disabled={!isOnline}
                  >
                    <Paperclip className="w-4 h-4" />
                  </Button>
                  <Input
                    ref={inputRef}
                    type="text"
                    placeholder={
                      isOnline
                        ? "Type your message..."
                        : "Waiting for connection..."
                    }
                    value={inputValue}
                    onChange={(e) =>
                      setInputValue(e.target.value)
                    }
                    className="flex-1 h-12"
                    aria-label="Chat message input"
                    disabled={!isOnline}
                  />
                  <Button
                    type="submit"
                    size="icon"
                    className="bg-[var(--primary)] hover:bg-[var(--primary-hover)] flex-shrink-0 h-12 w-12"
                    disabled={!inputValue.trim() || !isOnline}
                    aria-label="Send message"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </form>
                <div className="text-xs text-[var(--muted-foreground)] mt-2 text-center">
                  Powered by AI • Available 24/7 • Secure &
                  Confidential
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}