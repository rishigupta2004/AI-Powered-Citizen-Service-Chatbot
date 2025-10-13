import React, { useRef } from 'react';
import { motion, useScroll, useTransform } from 'motion/react';
import {
  ArrowRight,
  Shield,
  Globe,
  Users,
  Zap,
  Award,
  CheckCircle2,
  TrendingUp,
  Lock,
  Smartphone,
  Star,
  Clock,
  FileText,
  MessageSquare,
  User as UserIcon,
  Send,
} from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { ParticleBackground } from '../animations/ParticleBackground';
import { FloatingElements } from '../animations/FloatingElements';
import { GradientBlob } from '../animations/GradientBlob';
import { ServiceCard3D } from '../3d/ServiceCard3D';
import { Icon3D } from '../3d/Icon3D';
import { Card3D } from '../animations/Card3D';
import { Logo } from '../Logo';
import { getAllServices } from '../../data/servicesData';

interface EnhancedHomeProps {
  onNavigate: (page: string, serviceId?: string) => void;
}

export function EnhancedHome({ onNavigate }: EnhancedHomeProps) {
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ['start start', 'end start'],
  });

  const heroY = useTransform(scrollYProgress, [0, 1], ['0%', '30%']);
  const heroOpacity = useTransform(scrollYProgress, [0, 0.5], [1, 0.3]);
  const heroScale = useTransform(scrollYProgress, [0, 1], [1, 0.95]);

  const allServices = getAllServices();
  const featuredServices = allServices.slice(0, 6);

  const features = [
    {
      icon: Shield,
      title: 'Secure & Compliant',
      description: 'Bank-level encryption and government-grade security protocols',
      gradient: 'from-blue-500 to-blue-600',
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Process applications in minutes, not days',
      gradient: 'from-purple-500 to-purple-600',
    },
    {
      icon: Globe,
      title: 'Multi-Language',
      description: 'Available in 22+ regional languages',
      gradient: 'from-green-500 to-green-600',
    },
    {
      icon: Smartphone,
      title: 'Mobile First',
      description: 'Optimized for mobile devices and tablets',
      gradient: 'from-orange-500 to-orange-600',
    },
    {
      icon: Lock,
      title: 'Privacy Protected',
      description: 'Your data is encrypted and never shared',
      gradient: 'from-red-500 to-red-600',
    },
    {
      icon: Award,
      title: '24/7 Support',
      description: 'Round-the-clock assistance via chat, phone, and email',
      gradient: 'from-pink-500 to-pink-600',
    },
  ];

  const stats = [
    { value: '10M+', label: 'Active Users', icon: Users, color: 'from-blue-500 to-blue-600' },
    { value: '50+', label: 'Services', icon: Globe, color: 'from-purple-500 to-purple-600' },
    { value: '99.9%', label: 'Uptime', icon: TrendingUp, color: 'from-green-500 to-green-600' },
    { value: '24/7', label: 'Support', icon: Shield, color: 'from-orange-500 to-orange-600' },
  ];

  const testimonials = [
    {
      name: 'Rajesh Kumar',
      role: 'Business Owner',
      content: 'The passport renewal process was seamless. Received my passport in just 12 days!',
      rating: 5,
      avatar: 'RK',
    },
    {
      name: 'Priya Sharma',
      role: 'Student',
      content: 'Applied for my scholarship online and got approved within a week. Excellent service!',
      rating: 5,
      avatar: 'PS',
    },
    {
      name: 'Amit Patel',
      role: 'Professional',
      content: 'Updated my Aadhaar details from home. No need to visit the center. Very convenient!',
      rating: 5,
      avatar: 'AP',
    },
  ];

  const howItWorks = [
    {
      step: '1',
      title: 'Create Account',
      description: 'Sign up using your mobile number or Aadhaar',
      icon: Users,
      color: 'from-blue-500 to-blue-600',
    },
    {
      step: '2',
      title: 'Choose Service',
      description: 'Browse and select from 50+ government services',
      icon: FileText,
      color: 'from-purple-500 to-purple-600',
    },
    {
      step: '3',
      title: 'Submit Application',
      description: 'Fill the form and upload required documents',
      icon: CheckCircle2,
      color: 'from-green-500 to-green-600',
    },
    {
      step: '4',
      title: 'Track Status',
      description: 'Monitor your application in real-time',
      icon: Clock,
      color: 'from-orange-500 to-orange-600',
    },
  ];

  return (
    <div className="min-h-screen overflow-hidden bg-[var(--background)]">
      {/* Hero Section with Parallax */}
      <section
        ref={heroRef}
        className="relative min-h-screen flex items-center justify-center overflow-hidden"
      >
        {/* Animated Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#000080] via-[#000066] to-[#000050]">
          <ParticleBackground particleCount={60} />
          <FloatingElements count={10} />
          
          {/* Gradient Blobs */}
          <GradientBlob
            colors={['#FF9933', '#000080']}
            size={600}
            blur={100}
            opacity={0.3}
            speed={25}
            className="top-0 left-0"
          />
          <GradientBlob
            colors={['#138808', '#000080']}
            size={500}
            blur={90}
            opacity={0.25}
            speed={20}
            className="bottom-0 right-0"
          />
        </div>

        {/* Hero Content */}
        <motion.div
          style={{ y: heroY, opacity: heroOpacity, scale: heroScale }}
          className="relative z-10 max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)] text-center"
        >
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="mb-8"
          >
            <Logo size="xl" variant="white" showText={true} />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2, ease: 'easeOut' }}
          >
            <Badge className="mb-6 bg-white/10 text-white backdrop-blur-sm border-white/20 px-6 py-2 text-base">
              <span className="mr-2">🇮🇳</span>
              Digital India Initiative
            </Badge>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4, ease: 'easeOut' }}
            className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight"
          >
            Your Gateway to
            <br />
            <span className="bg-gradient-to-r from-[#FF9933] via-white to-[#138808] bg-clip-text text-transparent">
              Government Services
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6, ease: 'easeOut' }}
            className="text-xl md:text-2xl text-white/90 mb-12 max-w-3xl mx-auto leading-relaxed"
          >
            Access 50+ government services instantly. Fast, secure, and available 24/7.
            Your one-stop portal for all citizen services.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8, ease: 'easeOut' }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Button
              size="lg"
              className="bg-white text-[#000080] hover:bg-white/90 px-8 py-6 text-lg font-semibold shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25)] hover:scale-105 transition-all group"
              onClick={() => onNavigate('services')}
            >
              Explore Services
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-2 border-white text-white hover:bg-white hover:text-[#000080] px-8 py-6 text-lg font-semibold backdrop-blur-sm hover:scale-105 transition-all"
              onClick={() => onNavigate('dashboard')}
            >
              My Dashboard
            </Button>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1, ease: 'easeOut' }}
            className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20"
          >
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 1.2 + index * 0.1 }}
                className="relative group"
              >
                <div className="absolute inset-0 bg-white/10 rounded-[var(--radius-2xl)] backdrop-blur-sm blur-xl group-hover:blur-2xl transition-all" />
                <div className="relative bg-white/5 backdrop-blur-md border border-white/20 rounded-[var(--radius-2xl)] p-6 hover:bg-white/10 transition-all">
                  <stat.icon className="w-8 h-8 text-white mb-3 mx-auto" />
                  <div className="text-4xl font-bold text-white mb-2">{stat.value}</div>
                  <div className="text-white/80 text-sm">{stat.label}</div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.8, duration: 1 }}
          className="absolute bottom-10 left-1/2 -translate-x-1/2 z-20"
        >
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="w-6 h-10 border-2 border-white/50 rounded-full flex items-start justify-center p-2"
          >
            <motion.div
              animate={{ height: ['0%', '50%', '0%'] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="w-1 bg-white rounded-full"
            />
          </motion.div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="py-32 bg-gradient-to-b from-[var(--background)] to-[var(--background-secondary)] relative overflow-hidden">
        <FloatingElements count={5} className="opacity-20" />
        
        <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)] relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <Badge className="mb-4 bg-[#000080]/10 text-[#000080] border-[#000080]/20">
              Why Choose Us
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold text-[var(--foreground)] mb-4">
              Built for Citizens, By Government
            </h2>
            <p className="text-xl text-[var(--muted-foreground)] max-w-2xl mx-auto">
              Experience government services like never before with our modern, secure platform
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card3D intensity={8}>
                  <Card className="h-full border-2 border-[var(--card-border)] hover:border-[#000080] hover:shadow-[var(--shadow-12)] transition-all duration-300 bg-[var(--card)] group overflow-hidden">
                    <CardHeader>
                      <div className="mb-4">
                        <Icon3D icon={feature.icon} gradient={feature.gradient} size={64} />
                      </div>
                      <CardTitle className="text-xl group-hover:text-[#000080] transition-colors text-[var(--foreground)]">
                        {feature.title}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <CardDescription className="text-base text-[var(--muted-foreground)]">
                        {feature.description}
                      </CardDescription>
                    </CardContent>
                  </Card>
                </Card3D>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-32 bg-[var(--background-secondary)] relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)] relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <Badge className="mb-4 bg-[#138808]/10 text-[#138808] border-[#138808]/20">
              Simple Process
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold text-[var(--foreground)] mb-4">
              How It Works
            </h2>
            <p className="text-xl text-[var(--muted-foreground)] max-w-2xl mx-auto">
              Get started in just 4 easy steps
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {howItWorks.map((step, index) => (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.15 }}
                className="relative"
              >
                <Card className="h-full border-2 border-[var(--card-border)] bg-[var(--card)] hover:shadow-[var(--shadow-8)] transition-all group">
                  <CardHeader className="text-center">
                    <div className={`w-20 h-20 bg-gradient-to-br ${step.color} rounded-full flex items-center justify-center mx-auto mb-4 shadow-[var(--shadow-4)] group-hover:scale-110 transition-transform`}>
                      <step.icon className="w-10 h-10 text-white" />
                    </div>
                    <div className="text-sm font-semibold text-[var(--muted-foreground)] mb-2">
                      STEP {step.step}
                    </div>
                    <CardTitle className="text-xl text-[var(--foreground)]">{step.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="text-center">
                    <CardDescription className="text-base text-[var(--muted-foreground)]">
                      {step.description}
                    </CardDescription>
                  </CardContent>
                </Card>
                {index < howItWorks.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-[var(--muted)] to-transparent" />
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Services Section with 3D Cards */}
      <section className="py-32 bg-gradient-to-b from-[var(--background)] to-[var(--background-secondary)] relative overflow-hidden">
        <FloatingElements count={8} className="opacity-20" />
        
        <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)] relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <Badge className="mb-4 bg-[#FF9933]/10 text-[#FF9933] border-[#FF9933]/20">
              Popular Services
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold text-[var(--foreground)] mb-4">
              Most Requested Services
            </h2>
            <p className="text-xl text-[var(--muted-foreground)] max-w-2xl mx-auto">
              Quick access to the services you need most
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            {featuredServices.map((service, index) => (
              <motion.div
                key={service.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
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

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <Button
              size="lg"
              className="bg-[#000080] text-white hover:bg-[#000066] px-8"
              onClick={() => onNavigate('services')}
            >
              View All Services
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-32 bg-[var(--background-secondary)] relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)] relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <Badge className="mb-4 bg-purple-500/10 text-purple-600 border-purple-500/20">
              Testimonials
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold text-[var(--foreground)] mb-4">
              What Citizens Say
            </h2>
            <p className="text-xl text-[var(--muted-foreground)] max-w-2xl mx-auto">
              Real experiences from people using our services
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.15 }}
              >
                <Card className="h-full border-2 border-[var(--card-border)] bg-[var(--card)] hover:shadow-[var(--shadow-8)] transition-all">
                  <CardHeader>
                    <div className="flex items-center gap-1 mb-4">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                      ))}
                    </div>
                    <CardDescription className="text-base text-[var(--foreground)] italic leading-relaxed">
                      "{testimonial.content}"
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-[#000080] to-[#000066] rounded-full flex items-center justify-center text-white font-semibold">
                        {testimonial.avatar}
                      </div>
                      <div>
                        <div className="font-semibold text-[var(--foreground)]">{testimonial.name}</div>
                        <div className="text-sm text-[var(--muted-foreground)]">{testimonial.role}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Chatbot Showcase Section */}
      <section className="py-32 bg-gradient-to-b from-[var(--background-secondary)] to-[var(--background)] relative overflow-hidden">
        <FloatingElements count={6} className="opacity-20" />
        
        <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)] relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <Badge className="mb-4 bg-purple-500/10 text-purple-600 border-purple-500/20">
              AI-Powered Assistant
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold text-[var(--foreground)] mb-4">
              Meet Your Personal AI Assistant
            </h2>
            <p className="text-xl text-[var(--muted-foreground)] max-w-2xl mx-auto">
              Get instant help, apply for services, and track applications with our intelligent chatbot
            </p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left: Features */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="space-y-6"
            >
              {[
                {
                  icon: MessageSquare,
                  title: "Natural Conversations",
                  description: "Chat naturally in English or Hindi. Our AI understands context and provides relevant answers.",
                  color: "from-blue-500 to-blue-600",
                },
                {
                  icon: Zap,
                  title: "Instant Service Access",
                  description: "Apply for services, check status, and get documents without navigating menus.",
                  color: "from-purple-500 to-purple-600",
                },
                {
                  icon: Shield,
                  title: "Secure & Private",
                  description: "Your conversations are encrypted and never shared. Fully compliant with data protection laws.",
                  color: "from-green-500 to-green-600",
                },
                {
                  icon: Clock,
                  title: "24/7 Availability",
                  description: "Get help anytime, anywhere. Our AI never sleeps and responds in seconds.",
                  color: "from-orange-500 to-orange-600",
                },
              ].map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start gap-4 group"
                >
                  <div className={`w-14 h-14 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform shadow-lg`}>
                    <feature.icon className="w-7 h-7 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-[var(--foreground)] mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-[var(--muted-foreground)] leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </motion.div>
              ))}
            </motion.div>

            {/* Right: Chatbot Preview */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="relative">
                {/* Decorative elements */}
                <div className="absolute -inset-4 bg-gradient-to-r from-[#000080]/20 to-[#138808]/20 rounded-3xl blur-3xl" />
                
                {/* Preview Card */}
                <Card className="relative border-2 border-[var(--border)] shadow-2xl overflow-hidden bg-[var(--card)]">
                  <CardContent className="p-0">
                    {/* Mock chatbot header */}
                    <div className="bg-gradient-to-r from-[#000080] to-[#000066] px-6 py-4 flex items-center gap-3">
                      <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                        <MessageSquare className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <div className="text-white font-bold text-lg">Seva Sindhu AI</div>
                        <div className="flex items-center gap-2 text-xs text-white/90">
                          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                          Always Online
                        </div>
                      </div>
                    </div>

                    {/* Mock conversation */}
                    <div className="p-6 space-y-4 bg-gradient-to-b from-[var(--background)] to-[var(--background-secondary)] min-h-[400px]">
                      <div className="flex gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-[#000080] to-[#000066] rounded-full flex items-center justify-center flex-shrink-0">
                          <MessageSquare className="w-4 h-4 text-white" />
                        </div>
                        <div className="bg-[var(--card)] border-2 border-[var(--border)] rounded-2xl rounded-bl-sm px-4 py-3 shadow-md max-w-[80%]">
                          <p className="text-sm text-[var(--foreground)]">
                            Hello! How can I assist you with government services today?
                          </p>
                        </div>
                      </div>

                      <div className="flex gap-3 justify-end">
                        <div className="bg-gradient-to-br from-[#000080] to-[#000066] rounded-2xl rounded-br-sm px-4 py-3 shadow-md max-w-[80%]">
                          <p className="text-sm text-white">
                            I need to apply for a passport
                          </p>
                        </div>
                        <div className="w-8 h-8 bg-gradient-to-br from-[#FF9933] to-[#FF7700] rounded-full flex items-center justify-center flex-shrink-0">
                          <UserIcon className="w-4 h-4 text-white" />
                        </div>
                      </div>

                      <div className="flex gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-[#000080] to-[#000066] rounded-full flex items-center justify-center flex-shrink-0">
                          <MessageSquare className="w-4 h-4 text-white" />
                        </div>
                        <div className="bg-[var(--card)] border-2 border-[var(--border)] rounded-2xl rounded-bl-sm px-4 py-3 shadow-md max-w-[80%]">
                          <p className="text-sm text-[var(--foreground)] mb-3">
                            Great! I can help you with passport services. Here's what you need:
                          </p>
                          <Card className="border border-[var(--border)] bg-[var(--background)]/50">
                            <CardContent className="p-3">
                              <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                                  <FileText className="w-5 h-5 text-white" />
                                </div>
                                <div className="flex-1">
                                  <div className="font-semibold text-sm text-[var(--foreground)]">
                                    Passport Application
                                  </div>
                                  <div className="text-xs text-[var(--muted-foreground)]">
                                    15-20 days • ₹1,500
                                  </div>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                      </div>

                      <div className="absolute bottom-6 left-6 right-6">
                        <div className="flex gap-2 items-center p-3 bg-white dark:bg-gray-900 rounded-2xl border-2 border-[var(--border)] shadow-lg">
                          <input
                            type="text"
                            placeholder="Ask anything..."
                            className="flex-1 bg-transparent text-sm outline-none text-[var(--foreground)] placeholder:text-[var(--muted-foreground)]"
                            disabled
                          />
                          <div className="w-10 h-10 bg-gradient-to-br from-[#000080] to-[#000066] rounded-xl flex items-center justify-center">
                            <Send className="w-5 h-5 text-white" />
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Floating elements */}
                <motion.div
                  animate={{
                    y: [0, -20, 0],
                    rotate: [0, 5, 0],
                  }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                  className="absolute -top-8 -right-8 w-24 h-24 bg-gradient-to-br from-[#FF9933] to-[#FF7700] rounded-3xl opacity-20 blur-2xl"
                />
                <motion.div
                  animate={{
                    y: [0, 20, 0],
                    rotate: [0, -5, 0],
                  }}
                  transition={{
                    duration: 5,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 1,
                  }}
                  className="absolute -bottom-8 -left-8 w-32 h-32 bg-gradient-to-br from-[#138808] to-[#0F6606] rounded-3xl opacity-20 blur-2xl"
                />
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 bg-gradient-to-br from-[#000080] via-[#000066] to-[#000050] text-white relative overflow-hidden">
        <ParticleBackground particleCount={40} />
        <FloatingElements count={6} />
        
        <div className="max-w-4xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)] text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <MessageSquare className="w-16 h-16 text-white mx-auto mb-6" />
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Ready to Get Started?
            </h2>
            <p className="text-xl text-white/90 mb-12 max-w-2xl mx-auto">
              Join millions of citizens already using Seva Sindhu for seamless government services
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                size="lg"
                className="bg-white text-[#000080] hover:bg-white/90 px-8 py-6 text-lg font-semibold shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25)]"
                onClick={() => onNavigate('services')}
              >
                Explore Services
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="border-2 border-white text-white hover:bg-white hover:text-[#000080] px-8 py-6 text-lg font-semibold backdrop-blur-sm"
                onClick={() => onNavigate('about')}
              >
                Learn More
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
