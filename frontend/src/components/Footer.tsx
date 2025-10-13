import React from "react";
import {
  Facebook,
  Twitter,
  Instagram,
  Linkedin,
  Youtube,
  Mail,
  Phone,
  MapPin,
} from "lucide-react";
import { Separator } from "./ui/separator";
import { Logo } from "./Logo";

interface FooterProps {
  onNavigate: (page: string) => void;
}

export function Footer({ onNavigate }: FooterProps) {
  const currentYear = new Date().getFullYear();

  const quickLinks = [
    { label: "Home", page: "home" },
    { label: "Services", page: "services" },
    { label: "About Us", page: "about" },
    { label: "FAQ", page: "faq" },
  ];

  const services = [
    "Passport Services",
    "Aadhaar Services",
    "EPFO Services",
    "Scholarship Programs",
    "Driving License",
  ];

  const legal = [
    "Privacy Policy",
    "Terms of Service",
    "Cookie Policy",
    "Accessibility Statement",
    "RTI Information",
  ];

  const socialLinks = [
    { icon: Facebook, label: "Facebook", href: "#" },
    { icon: Twitter, label: "Twitter", href: "#" },
    { icon: Instagram, label: "Instagram", href: "#" },
    { icon: Linkedin, label: "LinkedIn", href: "#" },
    { icon: Youtube, label: "YouTube", href: "#" },
  ];

  return (
    <footer
      className="bg-gradient-to-b from-navy to-navy/95 text-white mt-20"
      role="contentinfo"
    >
      {/* Government Emblem Section */}
      <div className="border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-6">
              <Logo size="lg" variant="white" showText={true} />
              <div className="h-12 w-px bg-white/20" />
              <div>
                <div className="text-xl font-bold">
                  Government of India
                </div>
                <div className="text-sm text-white/70">
                  भारत सरकार
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center backdrop-blur-sm">
                <span className="text-2xl">🏛️</span>
              </div>
              <div className="text-sm text-white/70">
                <div>Digital India</div>
                <div>डिजिटल इंडिया</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-saffron">
              Quick Links
            </h3>
            <ul className="space-y-3" role="list">
              {quickLinks.map((link) => (
                <li key={link.page}>
                  <button
                    onClick={() => onNavigate(link.page)}
                    className="text-white/80 hover:text-white transition-colors hover:translate-x-1 inline-block"
                  >
                    → {link.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* Services */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-saffron">
              Popular Services
            </h3>
            <ul className="space-y-3" role="list">
              {services.map((service, index) => (
                <li key={index}>
                  <button className="text-white/80 hover:text-white transition-colors hover:translate-x-1 inline-block">
                    → {service}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Information */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-saffron">
              Contact Us
            </h3>
            <ul className="space-y-3" role="list">
              <li className="flex items-start gap-3">
                <Phone className="w-5 h-5 text-white/60 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-white/80">Toll-Free</div>
                  <div className="text-sm text-white/60">
                    1800-XXX-XXXX
                  </div>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <Mail className="w-5 h-5 text-white/60 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-white/80">Email</div>
                  <div className="text-sm text-white/60">
                    support@gov.in
                  </div>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-white/60 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="text-white/80">Address</div>
                  <div className="text-sm text-white/60">
                    New Delhi, India
                  </div>
                </div>
              </li>
            </ul>
          </div>

          {/* Social & Newsletter */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-saffron">
              Stay Connected
            </h3>
            <div className="flex gap-3 mb-6">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  className="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-lg flex items-center justify-center transition-all hover:scale-110 backdrop-blur-sm"
                  aria-label={social.label}
                >
                  <social.icon className="w-5 h-5" />
                </a>
              ))}
            </div>
            <div className="text-sm text-white/60">
              Follow us on social media for updates and
              announcements.
            </div>
          </div>
        </div>
      </div>

      <Separator className="bg-white/10" />

      {/* Legal Links */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-wrap items-center justify-center gap-6 mb-4">
          {legal.map((item, index) => (
            <button
              key={index}
              className="text-sm text-white/60 hover:text-white transition-colors"
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      <Separator className="bg-white/10" />

      {/* Bottom Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-white/60">
          <div className="flex items-center gap-2">
            <span>© {currentYear} Government of India.</span>
            <span className="hidden md:inline">
              All rights reserved.
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span>
              Content owned by Ministry of Electronics & IT
            </span>
            <span className="hidden md:inline">|</span>
            <span className="hidden md:inline">
              Last updated: {new Date().toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>

      {/* Accessibility Statement */}
      <div className="bg-white/5 border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="text-xs text-center text-white/50">
            This website is designed to be accessible and
            compliant with WCAG 2.1 Level AA standards.
            <button className="ml-2 underline hover:text-white/70 transition-colors">
              Report accessibility issues
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
}