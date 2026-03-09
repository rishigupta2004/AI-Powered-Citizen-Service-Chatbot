import React, { useRef, useState } from 'react';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import {
  ArrowRight,
  Shield,
  Globe,
  Zap,
  Lock,
  Smartphone,
  Search,
  CheckCircle2,
  Sparkles
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ServiceCard3D } from '../3d/ServiceCard3D';
import { getAllServices } from '../../data/servicesData';
import { AbstractCitizen } from '../../src/components/art/AbstractCitizen';
import { Mandala } from '../../src/components/art/Mandala';

interface EnhancedHomeProps {
  onNavigate: (page: string, serviceId?: string) => void;
}

export function EnhancedHome({ onNavigate }: EnhancedHomeProps) {
  const { t, i18n } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] });
  const heroY = useTransform(scrollYProgress, [0, 1], ['0%', '40%']);
  const heroOpacity = useTransform(scrollYProgress, [0, 0.8], [1, 0]);

  const allServices = getAllServices();
  const featuredServices = allServices.slice(0, 6);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onNavigate('services');
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAFA] dark:bg-[#0a0f1c] font-sans overflow-hidden">
      
      {/* 
        Sarvam-Style Vibrant Hero Section 
        Rich indigos, animated background art, massive bilingual typography
      */}
      <section ref={heroRef} className="relative pt-32 pb-40 min-h-[95vh] flex items-center justify-center overflow-hidden bg-gradient-to-br from-indigo-950 via-[#000080] to-purple-950">
        
        {/* Animated Background Art */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-40 mix-blend-screen">
          <div className="absolute top-[-10%] right-[-5%] opacity-50 mix-blend-color-dodge">
            <Mandala size={800} />
          </div>
          <div className="absolute bottom-[-20%] left-[-10%] opacity-30 mix-blend-color-dodge">
            <Mandala size={600} />
          </div>
          {/* Saffron/Green abstract glows */}
          <motion.div animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.6, 0.3] }} transition={{ duration: 8, repeat: Infinity }} className="absolute top-[20%] left-[10%] w-96 h-96 bg-saffron rounded-full blur-[120px]" />
          <motion.div animate={{ scale: [1, 1.3, 1], opacity: [0.2, 0.5, 0.2] }} transition={{ duration: 10, repeat: Infinity, delay: 2 }} className="absolute bottom-[10%] right-[20%] w-[30rem] h-[30rem] bg-green rounded-full blur-[150px]" />
        </div>

        {/* Floating Cartoon/Abstract Elements (Sarvam vibe) */}
        <div className="absolute left-[5%] top-[30%] w-32 h-32 hidden lg:block opacity-80 pointer-events-none drop-shadow-2xl">
          <AbstractCitizen color="#FF9933" />
        </div>
        <div className="absolute right-[8%] bottom-[20%] w-40 h-40 hidden lg:block opacity-80 pointer-events-none drop-shadow-2xl">
          <AbstractCitizen color="#138808" className="scale-x-[-1]" />
        </div>

        <motion.div style={{ y: heroY, opacity: heroOpacity }} className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center flex flex-col items-center">
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, type: "spring", bounce: 0.4 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/20 shadow-xl mb-8"
          >
            <Sparkles className="w-4 h-4 text-saffron" />
            <span className="text-sm font-bold tracking-widest text-white uppercase">
              {t("app.subtitle")}
            </span>
          </motion.div>

          <div className="relative mb-8">
            {/* Faded Background Translation (Big Indic Text) */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.15 }}
              transition={{ duration: 2 }}
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full text-9xl md:text-[12rem] font-bold text-white whitespace-nowrap pointer-events-none select-none font-display tracking-tighter"
            >
              {i18n.language !== 'hi' ? 'सेवा सिंधु' : 'Seva Sindhu'}
            </motion.div>

            {/* Main Foreground Text */}
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, type: "spring", bounce: 0.3, delay: 0.1 }}
              className="relative text-5xl md:text-7xl lg:text-8xl font-display font-extrabold text-white tracking-tight leading-[1.1]"
            >
              {t("app.title").split('-')[0].trim()}
            </motion.h1>
          </div>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
            className="text-lg md:text-2xl text-blue-100/90 mb-12 max-w-2xl leading-relaxed font-light backdrop-blur-sm"
          >
            {t("home.hero.subtitle", "Access 50+ government services instantly. Fast, secure, and available in your language.")}
          </motion.p>

          {/* Glowing Search Bar */}
          <motion.div
            initial={{ opacity: 0, y: 30, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="w-full max-w-2xl relative group"
          >
            <div className="absolute -inset-1.5 bg-gradient-to-r from-saffron via-white to-green rounded-full blur-md opacity-40 group-hover:opacity-70 transition duration-500"></div>
            <form onSubmit={handleSearch} className="relative flex items-center bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl rounded-full p-2.5 shadow-2xl">
              <Search className="absolute left-6 w-6 h-6 text-slate-400" />
              <Input
                type="text"
                placeholder={t("home.hero.searchPlaceholder", "Search for Passport, Aadhaar, Driving License...")}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-16 pr-40 h-14 text-lg bg-transparent border-0 focus-visible:ring-0 text-slate-900 dark:text-white placeholder:text-slate-400/70"
              />
              <Button
                type="submit"
                className="absolute right-2.5 h-12 px-8 rounded-full bg-gradient-to-r from-blue-700 to-indigo-700 hover:from-blue-600 hover:to-indigo-600 text-white font-bold shadow-lg transition-transform active:scale-95"
              >
                {t("home.hero.search", "Search")}
              </Button>
            </form>
          </motion.div>
        </motion.div>
      </section>

      {/* Services Grid with 3D Interaction */}
      <section className="py-32 relative z-20 -mt-10 bg-white dark:bg-[#0a0f1c] rounded-t-[3rem] shadow-[0_-20px_40px_rgba(0,0,0,0.1)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-display font-extrabold text-slate-900 dark:text-white mb-6">
              {t("home.services.title", "Popular Services")}
            </h2>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
            {featuredServices.map((service, index) => (
              <motion.div
                key={service.id}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.6, delay: index * 0.1, type: "spring", bounce: 0.4 }}
              >
                <ServiceCard3D
                  icon={service.icon}
                  name={service.name}
                  description={service.description}
                  badge={service.badge}
                  gradient={service.gradient}
                  processingTime={service.processingTime}
                  fee={service.fee}
                  onClick={() => onNavigate('service-detail', service.id)}
                />
              </motion.div>
            ))}
          </div>

          <div className="text-center">
            <Button
              size="lg"
              className="bg-indigo-950 text-white hover:bg-indigo-900 px-10 h-16 rounded-full text-lg font-bold shadow-xl transition-transform hover:-translate-y-1"
              onClick={() => onNavigate('services')}
            >
              {t("home.services.viewAll", "View All Services")}
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </div>
        </div>
      </section>

      {/* Dynamic Features Section */}
      <section className="py-32 bg-slate-50 dark:bg-slate-900/50 relative overflow-hidden">
        <div className="absolute top-0 w-full h-px bg-gradient-to-r from-transparent via-slate-300 dark:via-slate-700 to-transparent"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-display font-extrabold text-slate-900 dark:text-white">
              {t("home.features.title", "Why Choose Seva Sindhu")}
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: Shield,
                title: t("home.features.tracking.title", "Secure & Compliant"),
                desc: t("home.features.tracking.description", "Bank-level encryption and government-grade security protocols"),
                color: "text-blue-600", bg: "bg-blue-100 dark:bg-blue-900/40"
              },
              {
                icon: Zap,
                title: t("home.features.services.title", "Lightning Fast"),
                desc: t("home.features.services.description", "Process applications in minutes, not days"),
                color: "text-saffron", bg: "bg-orange-100 dark:bg-orange-900/40"
              },
              {
                icon: Globe,
                title: t("home.features.languages.title", "Multi-Language Support"),
                desc: t("home.features.languages.description", "Available in 22+ regional Indian languages"),
                color: "text-green-600", bg: "bg-green-100 dark:bg-green-900/40"
              }
            ].map((feat, i) => (
              <motion.div
                key={i}
                whileHover={{ y: -10 }}
                className="p-8 rounded-[2.5rem] bg-white dark:bg-slate-800 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 dark:border-slate-700 transition-all duration-300"
              >
                <div className={`w-16 h-16 rounded-2xl ${feat.bg} ${feat.color} flex items-center justify-center mb-6`}>
                  <feat.icon className="w-8 h-8" />
                </div>
                <h3 className="text-2xl font-bold font-display text-slate-900 dark:text-white mb-4">{feat.title}</h3>
                <p className="text-slate-500 dark:text-slate-400 leading-relaxed text-lg">{feat.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
