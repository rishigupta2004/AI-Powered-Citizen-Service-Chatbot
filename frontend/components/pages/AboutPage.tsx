import React from 'react';
import { motion } from 'framer-motion';
import {
  Shield,
  Users,
  TrendingUp,
  Award,
  CheckCircle2,
  Globe,
  Lock,
  Zap,
  Heart,
  Target,
  Building2,
  FileCheck,
  Phone,
  Mail,
  MapPin,
  ArrowRight,
  BookOpen,
  Landmark,
  Clock,
  Star,
  Layers,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Separator } from '../ui/separator';
import { Logo } from '../Logo';
import { FloatingElements } from '../animations/FloatingElements';
import { Card3D } from '../animations/Card3D';

interface AboutPageProps {
  onNavigate: (page: string) => void;
}

export function AboutPage({ onNavigate }: AboutPageProps) {
  const stats = [
    { icon: Users, value: '10M+', label: 'Active Citizens', color: 'from-blue-500 to-blue-600' },
    { icon: FileCheck, value: '50+', label: 'Government Services', color: 'from-orange-500 to-orange-600' },
    { icon: TrendingUp, value: '99.9%', label: 'System Uptime', color: 'from-green-500 to-green-600' },
    { icon: Award, value: '24/7', label: 'Citizen Support', color: 'from-purple-500 to-purple-600' },
  ];

  const objectives = [
    {
      icon: Target,
      title: 'Digital Transformation',
      description: 'Transform government service delivery through innovative digital solutions and seamless citizen experience.',
      color: 'from-blue-500 to-blue-600',
    },
    {
      icon: Users,
      title: 'Inclusive Access',
      description: 'Ensure every citizen, regardless of location or ability, can access government services with ease.',
      color: 'from-purple-500 to-purple-600',
    },
    {
      icon: Shield,
      title: 'Security & Privacy',
      description: 'Maintain the highest standards of data security and privacy protection for all citizen information.',
      color: 'from-green-500 to-green-600',
    },
    {
      icon: Zap,
      title: 'Efficiency & Speed',
      description: 'Reduce processing times and eliminate bureaucratic delays through automated workflows.',
      color: 'from-orange-500 to-orange-600',
    },
  ];

  const features = [
    {
      icon: Globe,
      title: 'Multi-Language Support',
      description: 'Available in 22+ official Indian languages for nationwide accessibility',
      color: 'from-blue-500 to-indigo-600',
    },
    {
      icon: Lock,
      title: 'Bank-Grade Security',
      description: '256-bit encryption and ISO 27001 certified infrastructure',
      color: 'from-green-500 to-teal-600',
    },
    {
      icon: Heart,
      title: 'Accessibility First',
      description: 'WCAG 2.1 AA compliant for citizens with disabilities',
      color: 'from-pink-500 to-rose-600',
    },
    {
      icon: Clock,
      title: 'Real-Time Tracking',
      description: 'Monitor your application status 24/7 with instant updates',
      color: 'from-orange-500 to-amber-600',
    },
    {
      icon: Star,
      title: 'User-Friendly Interface',
      description: 'Intuitive design tested with 10,000+ real users',
      color: 'from-yellow-500 to-orange-600',
    },
    {
      icon: Layers,
      title: 'Integrated Services',
      description: 'One-stop portal for all central and state services',
      color: 'from-purple-500 to-violet-600',
    },
  ];

  const partnerships = [
    { name: 'Ministry of Electronics & IT', type: 'Parent Ministry', icon: Landmark },
    { name: 'National Informatics Centre', type: 'Technology Partner', icon: Building2 },
    { name: 'UIDAI (Aadhaar)', type: 'Integration Partner', icon: Shield },
    { name: 'Digital India Corporation', type: 'Implementation Partner', icon: Globe },
    { name: 'State Governments', type: 'Service Providers', icon: Building2 },
    { name: 'Common Service Centers', type: 'Last Mile Delivery', icon: MapPin },
  ];

  const certifications = [
    'ISO 27001:2013 Information Security',
    'WCAG 2.1 Level AA Accessibility',
    'GIGW (Government of India Guidelines)',
    'IT Act 2000 Compliance',
    'SSL/TLS Encrypted Communication',
    'Regular Security Audits (CERT-In)',
    'Data Privacy & Protection Compliant',
    'Multi-Factor Authentication (MFA)',
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-[var(--background)] to-[var(--background-secondary)] pt-32 pb-20">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-[#000080] via-[#000066] to-[#000050] text-white py-20 overflow-hidden mb-20">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />
        </div>

        <FloatingElements count={6} className="opacity-20" />

        <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)] relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            {/* Logo */}
            <div className="flex justify-center mb-6">
              <Logo size="xl" variant="white" showText={true} />
            </div>

            {/* Badge */}
            <Badge className="mb-6 bg-white/10 text-white border-white/20 backdrop-blur-sm px-6 py-2 text-base">
              Government of India Initiative
            </Badge>

            {/* Title */}
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              Seva Sindhu Portal
            </h1>

            {/* Subtitle */}
            <p className="text-xl md:text-2xl text-white/90 max-w-4xl mx-auto leading-relaxed mb-4">
              An integrated digital platform empowering citizens with seamless access to government services across India
            </p>

            {/* Attribution */}
            <p className="text-lg text-white/80 max-w-3xl mx-auto">
              Developed under the Digital India programme in collaboration with Ministry of Electronics & Information Technology
            </p>
          </motion.div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-[var(--space-4)] sm:px-[var(--space-6)] lg:px-[var(--space-8)]">
        {/* Stats Grid */}
        <section className="mb-20">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <Card3D intensity={10}>
                  <Card className="text-center border-2 border-[var(--card-border)] shadow-[var(--shadow-8)] hover:shadow-[var(--shadow-12)] transition-all bg-[var(--card)]">
                    <CardHeader className="pb-4">
                      <div className={`w-16 h-16 bg-gradient-to-br ${stat.color} rounded-[var(--radius-2xl)] flex items-center justify-center mx-auto mb-4 shadow-[var(--shadow-4)]`}>
                        <stat.icon className="w-8 h-8 text-white" />
                      </div>
                      <div className="text-4xl font-bold text-[var(--foreground)]">{stat.value}</div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-[var(--muted-foreground)] font-medium">{stat.label}</p>
                    </CardContent>
                  </Card>
                </Card3D>
              </motion.div>
            ))}
          </div>
        </section>

        {/* About Section */}
        <section className="mb-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Card className="border-2 border-[var(--card-border)] shadow-[var(--shadow-8)] bg-[var(--card)]">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#000080] to-[#000066] rounded-[var(--radius-lg)] flex items-center justify-center">
                    <Landmark className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-3xl text-[var(--foreground)]">About Seva Sindhu</CardTitle>
                    <CardDescription className="text-lg text-[var(--muted-foreground)]">
                      Unified National Portal for Citizen Services
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <p className="text-lg text-[var(--foreground)] leading-relaxed">
                  <strong>Seva Sindhu</strong> (meaning "Ocean of Services") is a flagship digital initiative of the Government of India, 
                  designed to provide citizens with a unified platform for accessing various government services across 
                  central and state departments. Launched under the Digital India programme, the portal aims to transform 
                  governance through technology-enabled service delivery.
                </p>

                <Separator className="bg-[var(--border)]" />

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-xl font-bold text-[var(--foreground)] mb-3 flex items-center gap-2">
                      <Target className="w-5 h-5 text-[#FF9933]" />
                      Vision
                    </h3>
                    <p className="text-[var(--muted-foreground)] leading-relaxed">
                      To create a citizen-centric digital ecosystem that ensures transparent, efficient, and 
                      accessible government services for every Indian, regardless of geographical or socio-economic barriers.
                    </p>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-[var(--foreground)] mb-3 flex items-center gap-2">
                      <BookOpen className="w-5 h-5 text-[#138808]" />
                      Mission
                    </h3>
                    <p className="text-[var(--muted-foreground)] leading-relaxed">
                      To digitize and integrate government services across departments, eliminate paperwork, 
                      reduce processing times, and enhance transparency in public service delivery mechanisms.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </section>

        {/* Strategic Objectives */}
        <section className="mb-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl font-bold text-[var(--foreground)] mb-4">Strategic Objectives</h2>
            <p className="text-xl text-[var(--muted-foreground)] max-w-3xl mx-auto">
              Core goals driving our digital transformation initiative
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {objectives.map((objective, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="h-full border-2 border-[var(--card-border)] hover:border-[var(--primary)] hover:shadow-[var(--shadow-8)] transition-all bg-[var(--card)]">
                  <CardHeader>
                    <div className="flex items-start gap-4">
                      <div className={`w-14 h-14 bg-gradient-to-br ${objective.color} rounded-[var(--radius-xl)] flex items-center justify-center flex-shrink-0 shadow-[var(--shadow-4)]`}>
                        <objective.icon className="w-7 h-7 text-white" />
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-xl mb-2 text-[var(--foreground)]">{objective.title}</CardTitle>
                        <CardDescription className="text-base text-[var(--muted-foreground)]">
                          {objective.description}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Platform Features */}
        <section className="mb-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl font-bold text-[var(--foreground)] mb-4">Platform Features</h2>
            <p className="text-xl text-[var(--muted-foreground)] max-w-3xl mx-auto">
              Built with cutting-edge technology and citizen-first design principles
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="h-full text-center border-2 border-[var(--card-border)] hover:shadow-[var(--shadow-8)] transition-all bg-[var(--card)] group">
                  <CardHeader>
                    <div className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-[var(--radius-2xl)] flex items-center justify-center mx-auto mb-4 shadow-[var(--shadow-4)] group-hover:scale-110 transition-transform`}>
                      <feature.icon className="w-8 h-8 text-white" />
                    </div>
                    <CardTitle className="text-lg mb-2 text-[var(--foreground)]">{feature.title}</CardTitle>
                    <CardDescription className="text-sm text-[var(--muted-foreground)]">
                      {feature.description}
                    </CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Implementation Partners */}
        <section className="mb-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Card className="border-2 border-[var(--card-border)] shadow-[var(--shadow-8)] bg-gradient-to-br from-[var(--card)] to-[var(--background-secondary)]">
              <CardHeader>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#000080] to-[#000066] rounded-[var(--radius-lg)] flex items-center justify-center">
                    <Building2 className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-3xl text-[var(--foreground)]">Implementation Partners</CardTitle>
                    <CardDescription className="text-lg text-[var(--muted-foreground)]">
                      Collaborative ecosystem powering digital governance
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {partnerships.map((partner, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, scale: 0.95 }}
                      whileInView={{ opacity: 1, scale: 1 }}
                      viewport={{ once: true }}
                      transition={{ delay: index * 0.05 }}
                      className="p-4 bg-[var(--card)] border-2 border-[var(--border)] rounded-[var(--radius-lg)] hover:border-[var(--primary)] hover:shadow-[var(--shadow-4)] transition-all group"
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 bg-[var(--muted)]/50 rounded-[var(--radius-md)] flex items-center justify-center group-hover:bg-[var(--primary)] group-hover:text-white transition-colors">
                          <partner.icon className="w-5 h-5" />
                        </div>
                        <div className="flex-1">
                          <div className="font-semibold text-[var(--foreground)] text-sm">{partner.name}</div>
                          <div className="text-xs text-[var(--muted-foreground)]">{partner.type}</div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </section>

        {/* Compliance & Certifications */}
        <section className="mb-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Card className="border-2 border-[var(--card-border)] shadow-[var(--shadow-8)] bg-[var(--card)]">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-[var(--radius-lg)] flex items-center justify-center">
                    <Shield className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl text-[var(--foreground)]">Compliance & Standards</CardTitle>
                    <CardDescription className="text-[var(--muted-foreground)]">
                      Meeting international security and accessibility standards
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4">
                  {certifications.map((item, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <div className="w-6 h-6 bg-[#138808] rounded-full flex items-center justify-center flex-shrink-0">
                        <CheckCircle2 className="w-4 h-4 text-white" />
                      </div>
                      <span className="text-[var(--foreground)]">{item}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </section>

        {/* Contact Information */}
        <section className="mb-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Card className="border-2 border-[var(--card-border)] shadow-[var(--shadow-8)] bg-[var(--card)]">
              <CardHeader>
                <CardTitle className="text-2xl text-[var(--foreground)]">Contact Information</CardTitle>
                <CardDescription className="text-[var(--muted-foreground)]">
                  Reach out to us for support, feedback, or inquiries
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-blue-500/10 rounded-[var(--radius-lg)] flex items-center justify-center flex-shrink-0">
                      <Phone className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <div className="font-semibold text-[var(--foreground)] mb-1">Helpline</div>
                      <div className="text-[var(--muted-foreground)]">1800-XXX-XXXX</div>
                      <div className="text-sm text-[var(--muted-foreground)]">Mon-Sat: 8 AM - 8 PM</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-purple-500/10 rounded-[var(--radius-lg)] flex items-center justify-center flex-shrink-0">
                      <Mail className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                      <div className="font-semibold text-[var(--foreground)] mb-1">Email Support</div>
                      <div className="text-[var(--muted-foreground)] break-all">support@sevasindhu.gov.in</div>
                      <div className="text-sm text-[var(--muted-foreground)]">24-hour response time</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-green-500/10 rounded-[var(--radius-lg)] flex items-center justify-center flex-shrink-0">
                      <MapPin className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <div className="font-semibold text-[var(--foreground)] mb-1">Office Address</div>
                      <div className="text-[var(--muted-foreground)]">Electronics Niketan</div>
                      <div className="text-sm text-[var(--muted-foreground)]">New Delhi - 110003</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </section>

        {/* CTA Section */}
        <section>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Card className="border-2 border-[#000080] shadow-[var(--shadow-12)] bg-gradient-to-br from-[#000080] to-[#000066] text-white overflow-hidden relative">
              <div className="absolute inset-0 opacity-10">
                <div className="absolute inset-0" style={{
                  backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
                }} />
              </div>
              <CardContent className="relative z-10 py-12 text-center">
                <h2 className="text-3xl font-bold mb-4">Explore Our Services</h2>
                <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
                  Access 50+ government services from the comfort of your home
                </p>
                <div className="flex flex-wrap gap-4 justify-center">
                  <Button
                    size="lg"
                    className="bg-white text-[#000080] hover:bg-white/90 px-8 shadow-[var(--shadow-8)]"
                    onClick={() => onNavigate('services')}
                  >
                    Browse Services
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>
                  <Button
                    size="lg"
                    variant="outline"
                    className="border-2 border-white text-white hover:bg-white hover:text-[#000080] px-8"
                    onClick={() => onNavigate('faq')}
                  >
                    View FAQ
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </section>
      </div>
    </div>
  );
}
